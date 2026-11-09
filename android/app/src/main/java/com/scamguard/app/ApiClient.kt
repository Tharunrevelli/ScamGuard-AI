package com.scamguard.app

import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import java.net.ConnectException
import java.net.SocketTimeoutException
import java.net.UnknownHostException

/**
 * Mobile-to-Backend HTTP API Client.
 * Connects Android app to FastAPI backend with strict timeouts and robust offline handling.
 */
class ApiClient(private val baseUrl: String = "http://172.22.107.154:8000/api/v1") {

    sealed class Result<out T> {
        data class Success<out T>(val data: T) : Result<T>()
        data class Error(val message: String, val isOffline: Boolean = false) : Result<Nothing>()
    }

    fun detect(
        text: String,
        source: String = "MANUAL",
        sessionId: String = "android_client",
        bypassPrefilter: Boolean = true,
        redactPii: Boolean = true
    ): Result<DetectionResult> {
        val endpoint = "$baseUrl/detect"
        var conn: HttpURLConnection? = null

        return try {
            val url = URL(endpoint)
            conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/json; charset=UTF-8")
            conn.setRequestProperty("Accept", "application/json")
            conn.setRequestProperty("X-Session-ID", sessionId)
            conn.connectTimeout = 6000
            conn.readTimeout = 8000
            conn.doOutput = true

            val payload = JSONObject().apply {
                put("text", text)
                put("source", source)
                put("client_session_id", sessionId)
                put("bypass_prefilter", bypassPrefilter)
                put("redact_pii_before_analysis", redactPii)
            }

            OutputStreamWriter(conn.outputStream, "UTF-8").use { writer ->
                writer.write(payload.toString())
                writer.flush()
            }

            val statusCode = conn.responseCode
            if (statusCode in 200..299) {
                val responseText = BufferedReader(InputStreamReader(conn.inputStream, "UTF-8")).use { it.readText() }
                val json = JSONObject(responseText)
                Result.Success(DetectionResult.fromJson(json))
            } else {
                val errorText = try {
                    BufferedReader(InputStreamReader(conn.errorStream, "UTF-8")).use { it.readText() }
                } catch (e: Exception) {
                    "Server error HTTP $statusCode"
                }
                Result.Error("API Error ($statusCode): $errorText")
            }
        } catch (e: ConnectException) {
            Result.Error("Cannot connect to detection server. Is the backend running? (Offline)", isOffline = true)
        } catch (e: SocketTimeoutException) {
            Result.Error("Connection timed out waiting for server response.", isOffline = true)
        } catch (e: UnknownHostException) {
            Result.Error("Could not resolve server host. Check network connection.", isOffline = true)
        } catch (e: Exception) {
            Result.Error("Network error: ${e.localizedMessage ?: e.javaClass.simpleName}")
        } finally {
            conn?.disconnect()
        }
    }

    fun checkHealth(): Result<Boolean> {
        val endpoint = "$baseUrl/health"
        var conn: HttpURLConnection? = null
        return try {
            val url = URL(endpoint)
            conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "GET"
            conn.connectTimeout = 3000
            conn.readTimeout = 3000
            val code = conn.responseCode
            if (code == 200) Result.Success(true) else Result.Error("Health check returned HTTP $code")
        } catch (e: Exception) {
            Result.Error("Backend unreachable: ${e.message}", isOffline = true)
        } finally {
            conn?.disconnect()
        }
    }
}
