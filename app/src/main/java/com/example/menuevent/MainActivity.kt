package com.example.menuevent

import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.google.firebase.FirebaseApp
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.firestore.FirebaseFirestore
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import androidx.compose.runtime.rememberCoroutineScope
import com.example.menuevent.ui.theme.MenuEventTheme
import kotlinx.coroutines.tasks.await
import com.google.firebase.Timestamp
import android.content.Context
import androidx.compose.ui.platform.LocalContext
import androidx.compose.foundation.background
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Date
import java.util.Locale
import androidx.compose.runtime.DisposableEffect
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.clickable
import androidx.compose.foundation.BorderStroke

// Modèles de données simples pour les sélections
data class Event(val name: String, val stands: List<String>)

// Classe de données pour sauvegarder la sélection dans Firestore
data class SeatSelection(
    val evenement: String = "",
    val tribune: String = "",
    val rang: Int = 0,
    val numeroDePlace: Int = 0,
    val timestamp: Timestamp = Timestamp.now(),
    val userId: String = ""
)

// Modèles de données pour les animations
data class AnimationFrame(
    val frameUrl: String
)

// Legacy AnimationUser for backward compatibility
data class LegacyAnimationUser(
    val frames: List<String>
)

data class AnimationData(
    val animationId: String,
    val frameRate: Int,
    val frameCount: Int,
    val users: Map<String, LegacyAnimationUser>
)

data class AnimationConfig(
    val animationStartTime: String,
    val eventType: String,
    val animationType: String,
    val animationData: AnimationData,
    val status: String
)

data class UserSeat(
    val event: String,
    val stand: String,
    val row: Int,
    val seat: Int,
    val userId: String
)

data class UserAnimationPackage(
    val userId: String,
    val animationType: String,
    val eventType: String,
    val startTime: String,
    val endTime: String,
    val frames: List<String>,
    val frameRate: Int,
    val frameCount: Int,
    val isActive: Boolean,
    val isExpired: Boolean = false,
    val animationId: String = "",
    val duration: Double = 0.0,
    val pattern: String = "",
    val createdAt: String = ""
)

// New data models for synchronized animations
data class SynchronizedAnimation(
    val animationId: String,
    val animationType: String,
    val eventType: String,
    val startTime: String,
    val frameRate: Int,
    val frameCount: Int,
    val duration: Double,
    val active: Boolean,
    val createdAt: String,
    val updatedAt: String,
    val totalUsers: Int,
    val pattern: String
)

// New data models for color animations
data class ColorFrame(
    val r: Int,
    val g: Int,
    val b: Int
)

data class ColorAnimationUser(
    val colors: List<ColorFrame>,
    val startTime: String,
    val frameCount: Int
)

data class AnimationUser(
    val userId: String,
    val animationId: String,
    val animationType: String,
    val frames: List<String>,
    val startTime: String,
    val frameRate: Int,
    val frameCount: Int,
    val createdAt: String
)

data class ScheduledAnimation(
    val animationType: String,
    val eventType: String,
    val startTime: String,
    val endTime: String,
    val isActive: Boolean,
    val isExpired: Boolean = false
) {
    companion object {
        fun calculateEndTime(startTime: String, frameCount: Int, frameRate: Int): String {
            return try {
                Log.d("Animation", "Calculating end time: startTime=$startTime, frameCount=$frameCount, frameRate=$frameRate")
                
                // Parse the start time - handle both formats from web interface
                val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
                val startTimeFormatted = if (startTime.contains("T") && startTime.length <= 16) {
                    // Format from HTML datetime-local input: "2024-01-15T20:30"
                    startTime + ":00" // Add seconds if missing
                } else {
                    startTime
                }
                
                val startDate = dateFormat.parse(startTimeFormatted)
                val durationSeconds = frameCount.toDouble() / frameRate.toDouble()
                Log.d("Animation", "Animation duration: ${durationSeconds} seconds")
                
                val calendar = Calendar.getInstance()
                calendar.time = startDate
                calendar.add(Calendar.SECOND, durationSeconds.toInt())
                
                val result = dateFormat.format(calendar.time)
                Log.d("Animation", "Calculated end time: $result")
                result
            } catch (e: Exception) {
                Log.e("Animation", "Error calculating end time: ${e.message}")
                Log.e("Animation", "Start time format: $startTime")
                startTime // Fallback to start time if calculation fails
            }
        }
        
        fun isAnimationExpired(endTime: String): Boolean {
            return try {
                val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
                val endDate = dateFormat.parse(endTime)
                val currentDate = Date()
                val isExpired = currentDate.after(endDate)
                Log.d("Animation", "Animation expiry check: current=$currentDate, end=$endDate, expired=$isExpired")
                isExpired
            } catch (e: Exception) {
                Log.e("Animation", "Error checking expiration: ${e.message}")
                false // If we can't parse, assume not expired
            }
        }
    }
}

class MainActivity : ComponentActivity() {

    // Données de démonstration pour les événements et les tribunes
    val events = listOf(
        Event("Stade de foot", listOf("Tribune Nord", "Tribune Sud", "Tribune Est", "Tribune Ouest")),
        Event("Salle de concert", listOf("Balcon", "Orchestre", "Mezzanine")),
        Event("Théâtre", listOf("Parterre", "Corbeille", "Poulailler"))
    )

    private lateinit var auth: FirebaseAuth
    private lateinit var db: FirebaseFirestore
    private val httpClient = OkHttpClient()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        FirebaseApp.initializeApp(this)
        auth = FirebaseAuth.getInstance()
        db = FirebaseFirestore.getInstance()
        
        setContent {
            MenuEventTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    MainScreen(
                        events = events, 
                        auth = auth, 
                        db = db, 
                        httpClient = httpClient,
                        context = this@MainActivity
                    )
                }
            }
        }
    }

    // Fonction pour récupérer la configuration d'animation active
    private suspend fun getActiveAnimationConfig(): AnimationConfig? {
        return withContext(Dispatchers.IO) {
            try {
                val request = Request.Builder()
                    .url("https://us-central1-data-base-test-6ef5f.cloudfunctions.net/getActiveConfig")
                    .get()
                    .build()

                val response = httpClient.newCall(request).execute()
                if (response.isSuccessful) {
                    val responseBody = response.body?.string()
                    if (responseBody != null) {
                        val jsonObject = JSONObject(responseBody)
                        return@withContext parseAnimationConfig(jsonObject)
                    }
                }
                null
            } catch (e: Exception) {
                Log.e("Animation", "Error fetching active config: ${e.message}")
                null
            }
        }
    }

    // Fonction pour déclencher une animation
    private suspend fun triggerAnimation(animationType: String, userId: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val jsonBody = JSONObject()
                jsonBody.put("animationType", animationType)
                jsonBody.put("userId", userId)

                val requestBody = jsonBody.toString()
                    .toRequestBody("application/json".toMediaType())

                val request = Request.Builder()
                    .url("https://us-central1-data-base-test-6ef5f.cloudfunctions.net/triggerAnimation")
                    .post(requestBody)
                    .build()

                val response = httpClient.newCall(request).execute()
                response.isSuccessful
            } catch (e: Exception) {
                Log.e("Animation", "Error triggering animation: ${e.message}")
                false
            }
        }
    }

    private fun parseAnimationConfig(jsonObject: JSONObject): AnimationConfig {
        val animationDataJson = jsonObject.getJSONObject("animationData")
        val usersJson = animationDataJson.getJSONObject("users")
        
        val users = mutableMapOf<String, LegacyAnimationUser>()
        usersJson.keys().forEach { key ->
            val userJson = usersJson.getJSONObject(key)
            val framesArray = userJson.getJSONArray("frames")
            val frames = mutableListOf<String>()
            for (i in 0 until framesArray.length()) {
                frames.add(framesArray.getString(i))
            }
            users[key] = LegacyAnimationUser(frames)
        }

        val animationData = AnimationData(
            animationId = animationDataJson.getString("animationId"),
            frameRate = animationDataJson.getInt("frameRate"),
            frameCount = animationDataJson.getInt("frameCount"),
            users = users
        )

        return AnimationConfig(
            animationStartTime = jsonObject.getString("animationStartTime"),
            eventType = jsonObject.getString("eventType"),
            animationType = jsonObject.getString("animationType"),
            animationData = animationData,
            status = jsonObject.getString("status")
        )
    }

    companion object {
        // Fonction pour générer l'ID utilisateur basé sur la position du siège
        fun generateUserId(row: Int, seat: Int): String {
            return "user_${row}_${seat}"
        }
        
        // Fonction pour extraire le package d'animation pour un utilisateur spécifique
        suspend fun getUserAnimationPackage(
            httpClient: OkHttpClient,
            userSeat: UserSeat
        ): UserAnimationPackage? {
            return withContext(Dispatchers.IO) {
                try {
                    val userId = generateUserId(userSeat.row, userSeat.seat)
                    Log.d("Animation", "🔍 STARTING: Getting animation package for user: $userId")
                    Log.d("Animation", "User seat details: event=${userSeat.event}, row=${userSeat.row}, seat=${userSeat.seat}")
                    
                    // D'abord, essayer via HTTP (si les fonctions Cloud sont déployées)
                    Log.d("Animation", "🌐 Trying HTTP method first...")
                    val httpResult = getUserAnimationPackageHttp(httpClient, userId, userSeat)
                    if (httpResult != null) {
                        Log.d("Animation", "✅ HTTP method successful: ${httpResult.frames.size} frames")
                        return@withContext httpResult
                    } else {
                        Log.d("Animation", "❌ HTTP method failed, trying Firestore fallback...")
                    }
                    
                    // Fallback: accès direct à Firestore
                    Log.d("Animation", "🔥 Trying Firestore method...")
                    val firestoreResult = getUserAnimationPackageFirestore(userId, userSeat)
                    if (firestoreResult != null) {
                        Log.d("Animation", "✅ Firestore method successful: ${firestoreResult.frames.size} frames")
                    } else {
                        Log.d("Animation", "❌ Firestore method failed")
                    }
                    return@withContext firestoreResult
                } catch (e: Exception) {
                    Log.e("Animation", "💥 CRITICAL ERROR getting user animation package: ${e.message}", e)
                    null
                }
            }
        }
        
        // Fonction HTTP pour obtenir le package d'animation utilisateur
        private suspend fun getUserAnimationPackageHttp(
            httpClient: OkHttpClient,
            userId: String,
            userSeat: UserSeat
        ): UserAnimationPackage? {
            return try {
                Log.d("Animation", "🌐 HTTP: Trying to get package for $userId")
                val request = Request.Builder()
                    .url("https://us-central1-data-base-test-6ef5f.cloudfunctions.net/getActiveConfig")
                    .get()
                    .build()

                val response = httpClient.newCall(request).execute()
                Log.d("Animation", "🌐 HTTP: Response code: ${response.code}")
                
                if (response.isSuccessful) {
                    val responseBody = response.body?.string()
                    Log.d("Animation", "🌐 HTTP: Got response body: ${responseBody?.take(100)}...")
                    if (responseBody != null) {
                        val jsonObject = JSONObject(responseBody)
                        return extractUserPackageFromJson(jsonObject, userId, userSeat)
                    }
                } else {
                    Log.d("Animation", "🌐 HTTP: Failed with code ${response.code}")
                }
                null
            } catch (e: Exception) {
                Log.e("Animation", "🌐 HTTP: Error getting user package: ${e.message}")
                null
            }
        }
        
        // Fonction Firestore pour obtenir le package d'animation utilisateur
        private suspend fun getUserAnimationPackageFirestore(
            userId: String,
            userSeat: UserSeat
        ): UserAnimationPackage? {
            return try {
                Log.d("Animation", "=== DEBUGGING USER PACKAGE FETCH ===")
                Log.d("Animation", "Querying Firestore for user animation package: $userId")
                Log.d("Animation", "User seat: event=${userSeat.event}, row=${userSeat.row}, seat=${userSeat.seat}")
                
                val eventTypeForAnimation = when (userSeat.event) {
                    "Stade de foot" -> "football_stadium"
                    "Salle de concert" -> "concert_hall"
                    "Théâtre" -> "theater"
                    else -> "general"
                }
                
                Log.d("Animation", "Event type for animation: $eventTypeForAnimation")
                
                val db = FirebaseFirestore.getInstance()
                val task = db.collection("animation_configs")
                    .whereEqualTo("status", "active")
                    .get()
                    .await()
                
                Log.d("Animation", "Found ${task.documents.size} active configs")
                
                var mostRecentPackage: UserAnimationPackage? = null
                var mostRecentTimestamp: Long = 0
                
                for (document in task.documents) {
                    val data = document.data
                    if (data != null) {
                        val configEventType = data["eventType"] as? String ?: ""
                        val animationType = data["animationType"] as? String ?: ""
                        
                        Log.d("Animation", "Processing config: eventType=$configEventType, animationType=$animationType")
                        
                        if (configEventType == eventTypeForAnimation || configEventType == "all") {
                            Log.d("Animation", "Event type matches! Processing animation data...")
                            
                            val animationDataMap = data["animationData"] as? Map<String, Any>
                            if (animationDataMap != null) {
                                Log.d("Animation", "Animation data found: ${animationDataMap.keys}")
                                
                                val usersMap = animationDataMap["users"] as? Map<String, Any>
                                if (usersMap != null) {
                                    Log.d("Animation", "Users in animation: ${usersMap.keys}")
                                    
                                    val userFrames = usersMap[userId] as? Map<String, Any>
                                    if (userFrames != null) {
                                        Log.d("Animation", "Found frames for user $userId!")
                                        
                                        val frames = userFrames["frames"] as? List<String> ?: listOf()
                                        val frameCount = (animationDataMap["frameCount"] as? Number)?.toInt() ?: 80
                                        val frameRate = (animationDataMap["frameRate"] as? Number)?.toInt() ?: 15
                                        val startTime = data["animationStartTime"] as? String ?: ""
                                        
                                        Log.d("Animation", "Frame data: ${frames.size} frames, $frameRate fps, $frameCount total")
                                        
                                        val endTime = ScheduledAnimation.calculateEndTime(startTime, frameCount, frameRate)
                                        val isExpired = ScheduledAnimation.isAnimationExpired(endTime)
                                        
                                        Log.d("Animation", "Time data: start=$startTime, end=$endTime, expired=$isExpired")
                                        
                                        if (!isExpired) {
                                            val createdAtTimestamp = data["createdAt"] as? com.google.firebase.Timestamp
                                            val timestamp = createdAtTimestamp?.toDate()?.time ?: 0
                                            
                                            if (timestamp > mostRecentTimestamp) {
                                                mostRecentTimestamp = timestamp
                                                mostRecentPackage = UserAnimationPackage(
                                                    userId = userId,
                                                    animationType = animationType,
                                                    eventType = configEventType,
                                                    startTime = startTime,
                                                    endTime = endTime,
                                                    frames = frames,
                                                    frameRate = frameRate,
                                                    frameCount = frameCount,
                                                    isActive = true,
                                                    isExpired = false
                                                )
                                                Log.d("Animation", "Created user package for $userId with ${frames.size} frames")
                                            }
                                        } else {
                                            Log.d("Animation", "Animation is expired, skipping")
                                        }
                                    } else {
                                        Log.d("Animation", "No frames found for user $userId in animation")
                                        Log.d("Animation", "Available users: ${usersMap.keys}")
                                    }
                                } else {
                                    Log.d("Animation", "No users map found in animation data")
                                }
                            } else {
                                Log.d("Animation", "No animation data found in config")
                            }
                        } else {
                            Log.d("Animation", "Event type doesn't match: config=$configEventType, user=$eventTypeForAnimation")
                        }
                    }
                }
                
                if (mostRecentPackage != null) {
                    Log.d("Animation", "✅ SUCCESS: Found animation package for $userId: ${mostRecentPackage.frames.size} frames")
                } else {
                    Log.d("Animation", "❌ FAILED: No animation package found for user $userId")
                }
                
                Log.d("Animation", "=== END DEBUGGING USER PACKAGE FETCH ===")
                mostRecentPackage
            } catch (e: Exception) {
                Log.e("Animation", "❌ ERROR querying Firestore for user package: ${e.message}", e)
                null
            }
        }
        
        // Fonction pour extraire le package utilisateur depuis JSON
        private fun extractUserPackageFromJson(
            jsonObject: JSONObject,
            userId: String,
            userSeat: UserSeat
        ): UserAnimationPackage? {
            return try {
                val animationDataJson = jsonObject.getJSONObject("animationData")
                val usersJson = animationDataJson.getJSONObject("users")
                
                if (usersJson.has(userId)) {
                    val userJson = usersJson.getJSONObject(userId)
                    val framesArray = userJson.getJSONArray("frames")
                    val frames = mutableListOf<String>()
                    for (i in 0 until framesArray.length()) {
                        frames.add(framesArray.getString(i))
                    }
                    
                    val frameCount = animationDataJson.getInt("frameCount")
                    val frameRate = animationDataJson.getInt("frameRate")
                    val startTime = jsonObject.getString("animationStartTime")
                    val endTime = ScheduledAnimation.calculateEndTime(startTime, frameCount, frameRate)
                    val isExpired = ScheduledAnimation.isAnimationExpired(endTime)
                    
                    if (!isExpired) {
                        UserAnimationPackage(
                            userId = userId,
                            animationType = jsonObject.getString("animationType"),
                            eventType = jsonObject.getString("eventType"),
                            startTime = startTime,
                            endTime = endTime,
                            frames = frames,
                            frameRate = frameRate,
                            frameCount = frameCount,
                            isActive = true,
                            isExpired = false
                        )
                    } else {
                        Log.d("Animation", "Animation expired for user $userId")
                        null
                    }
                } else {
                    Log.d("Animation", "No animation data found for user $userId")
                    null
                }
            } catch (e: Exception) {
                Log.e("Animation", "Error extracting user package from JSON: ${e.message}")
                null
            }
        }
        
        // Fonction helper pour obtenir la configuration d'animation
        suspend fun getActiveAnimationConfig(httpClient: OkHttpClient): AnimationConfig? {
            return withContext(Dispatchers.IO) {
                try {
                    val request = Request.Builder()
                        .url("https://us-central1-data-base-test-6ef5f.cloudfunctions.net/getActiveConfig")
                        .get()
                        .build()

                    val response = httpClient.newCall(request).execute()
                    if (response.isSuccessful) {
                        val responseBody = response.body?.string()
                        if (responseBody != null) {
                            val jsonObject = JSONObject(responseBody)
                            return@withContext parseAnimationConfig(jsonObject)
                        }
                    } else {
                        Log.e("Animation", "HTTP Error: ${response.code} - ${response.message}")
                        Log.e("Animation", "Functions not deployed, trying direct Firestore query...")
                        
                        // Fallback: Try direct Firestore query since Cloud Functions are not deployed
                        return@withContext getActiveAnimationConfigFirestore()
                    }
                    null
                } catch (e: Exception) {
                    Log.e("Animation", "Error fetching active config: ${e.message}")
                    Log.e("Animation", "Trying direct Firestore query...")
                    
                    // Fallback: Try direct Firestore query
                    return@withContext getActiveAnimationConfigFirestore()
                }
            }
        }

        // Fonction de fallback pour obtenir la configuration d'animation directement de Firestore
        suspend fun getActiveAnimationConfigFirestore(): AnimationConfig? {
            return withContext(Dispatchers.IO) {
                try {
                    Log.d("Animation", "Querying Firestore directly for active animation config")
                    
                    val db = FirebaseFirestore.getInstance()
                    val task = db.collection("animation_configs")
                        .whereEqualTo("status", "active")
                        .get()
                        .await()
                    
                    Log.d("Animation", "Firestore query completed. Found ${task.documents.size} active configs")
                    
                    for (document in task.documents) {
                        val data = document.data
                        if (data != null) {
                            Log.d("Animation", "Found active config in Firestore")
                            
                            // Convert Firestore data to AnimationConfig
                            val animationDataMap = data["animationData"] as? Map<String, Any>
                            if (animationDataMap != null) {
                                val usersMap = animationDataMap["users"] as? Map<String, Any>
                                val users = mutableMapOf<String, LegacyAnimationUser>()
                                
                                usersMap?.forEach { (userId, userData) ->
                                    val userDataMap = userData as? Map<String, Any>
                                    val frames = userDataMap?.get("frames") as? List<String> ?: listOf()
                                    users[userId] = LegacyAnimationUser(frames)
                                }
                                
                                val animationData = AnimationData(
                                    animationId = animationDataMap["animationId"] as? String ?: "",
                                    frameRate = (animationDataMap["frameRate"] as? Number)?.toInt() ?: 15,
                                    frameCount = (animationDataMap["frameCount"] as? Number)?.toInt() ?: 80,
                                    users = users
                                )
                                
                                return@withContext AnimationConfig(
                                    animationStartTime = data["animationStartTime"] as? String ?: "",
                                    eventType = data["eventType"] as? String ?: "",
                                    animationType = data["animationType"] as? String ?: "",
                                    animationData = animationData,
                                    status = data["status"] as? String ?: ""
                                )
                            }
                        }
                    }
                    
                    Log.d("Animation", "No active animation config found in Firestore")
                    null
                } catch (e: Exception) {
                    Log.e("Animation", "Error querying Firestore for active config: ${e.message}", e)
                    null
                }
            }
        }

        // Fonction helper pour déclencher une animation
        suspend fun triggerAnimation(
            httpClient: OkHttpClient,
            animationType: String, 
            userId: String
        ): Boolean {
            return withContext(Dispatchers.IO) {
                try {
                    val jsonBody = JSONObject()
                    jsonBody.put("animationType", animationType)
                    jsonBody.put("userId", userId)

                    val requestBody = jsonBody.toString()
                        .toRequestBody("application/json".toMediaType())

                    val request = Request.Builder()
                        .url("https://us-central1-data-base-test-6ef5f.cloudfunctions.net/triggerAnimation")
                        .post(requestBody)
                        .build()

                    val response = httpClient.newCall(request).execute()
                    response.isSuccessful
                } catch (e: Exception) {
                    Log.e("Animation", "Error triggering animation: ${e.message}")
                    false
                }
            }
        }

        // Fonction pour vérifier les animations programmées pour un événement spécifique
        suspend fun checkScheduledAnimations(
            httpClient: OkHttpClient,
            eventType: String
        ): ScheduledAnimation? {
            return withContext(Dispatchers.IO) {
                try {
                    Log.d("Animation", "Checking scheduled animations for eventType: $eventType")
                    val request = Request.Builder()
                        .url("https://us-central1-data-base-test-6ef5f.cloudfunctions.net/getActiveConfig")
                        .get()
                        .build()

                    val response = httpClient.newCall(request).execute()
                    Log.d("Animation", "Response code: ${response.code}")
                    
                    if (response.isSuccessful) {
                        val responseBody = response.body?.string()
                        Log.d("Animation", "Response body: $responseBody")
                        
                        if (responseBody != null) {
                            val jsonObject = JSONObject(responseBody)
                            val configEventType = jsonObject.getString("eventType")
                            val configStatus = jsonObject.getString("status")
                            
                            Log.d("Animation", "Config eventType: $configEventType, status: $configStatus")
                            Log.d("Animation", "User eventType: $eventType")
                            
                            // Vérifier si l'animation correspond au type d'événement de l'utilisateur
                            if (configEventType == eventType || configEventType == "all") {
                                Log.d("Animation", "Event types match! Creating ScheduledAnimation")
                                
                                // Extraire les données d'animation pour calculer le temps de fin
                                val animationDataJson = jsonObject.getJSONObject("animationData")
                                val frameCount = animationDataJson.getInt("frameCount")
                                val frameRate = animationDataJson.getInt("frameRate")
                                val startTime = jsonObject.getString("animationStartTime")
                                
                                // Calculer le temps de fin
                                val endTime = ScheduledAnimation.calculateEndTime(startTime, frameCount, frameRate)
                                val isExpired = ScheduledAnimation.isAnimationExpired(endTime)
                                
                                Log.d("Animation", "Animation details: startTime=$startTime, endTime=$endTime, isExpired=$isExpired")
                                
                                // Si l'animation a expiré, ne pas la retourner
                                if (isExpired) {
                                    Log.d("Animation", "Animation expired, not returning")
                                    return@withContext null
                                }
                                
                                return@withContext ScheduledAnimation(
                                    animationType = jsonObject.getString("animationType"),
                                    eventType = configEventType,
                                    startTime = startTime,
                                    endTime = endTime,
                                    isActive = jsonObject.getString("status") == "active",
                                    isExpired = isExpired
                                )
                            } else {
                                Log.d("Animation", "Event types don't match. Config: $configEventType, User: $eventType")
                            }
                        }
                    } else {
                        Log.e("Animation", "HTTP Error: ${response.code} - ${response.message}")
                        Log.e("Animation", "Functions not deployed, trying direct Firestore query...")
                        
                        // Fallback: Try direct Firestore query since Cloud Functions are not deployed
                        return@withContext checkScheduledAnimationsFirestore(eventType)
                    }
                    null
                } catch (e: Exception) {
                    Log.e("Animation", "Error checking scheduled animations: ${e.message}", e)
                    Log.e("Animation", "Trying direct Firestore query...")
                    
                    // Fallback: Try direct Firestore query
                    return@withContext checkScheduledAnimationsFirestore(eventType)
                }
            }
        }

        // Fonction de fallback pour accéder directement à Firestore
        suspend fun checkScheduledAnimationsFirestore(eventType: String): ScheduledAnimation? {
            return withContext(Dispatchers.IO) {
                try {
                    Log.d("Animation", "Querying Firestore directly for eventType: $eventType")
                    
                    val db = FirebaseFirestore.getInstance()
                    val task = db.collection("animation_configs")
                        .whereEqualTo("status", "active")
                        .get()
                        .await()
                    
                    Log.d("Animation", "Firestore query completed. Found ${task.documents.size} active configs")
                    
                    var mostRecentAnimation: ScheduledAnimation? = null
                    var mostRecentTimestamp: Long = 0
                    
                    for (document in task.documents) {
                        val data = document.data
                        if (data != null) {
                            val configEventType = data["eventType"] as? String ?: ""
                            val configStatus = data["status"] as? String ?: ""
                            
                            Log.d("Animation", "Firestore config: eventType=$configEventType, status=$configStatus")
                            
                            // Vérifier si l'animation correspond au type d'événement de l'utilisateur
                            if (configEventType == eventType || configEventType == "all") {
                                Log.d("Animation", "Event types match! Processing animation from Firestore")
                                
                                // Extraire les données d'animation pour calculer le temps de fin
                                val animationDataMap = data["animationData"] as? Map<String, Any>
                                val frameCount = (animationDataMap?.get("frameCount") as? Number)?.toInt() ?: 80
                                val frameRate = (animationDataMap?.get("frameRate") as? Number)?.toInt() ?: 15
                                val startTime = data["animationStartTime"] as? String ?: ""
                                
                                // Calculer le temps de fin
                                val endTime = ScheduledAnimation.calculateEndTime(startTime, frameCount, frameRate)
                                val isExpired = ScheduledAnimation.isAnimationExpired(endTime)
                                
                                Log.d("Animation", "Animation details: startTime=$startTime, endTime=$endTime, isExpired=$isExpired")
                                
                                // Si l'animation a expiré, la passer et marquer comme inactive dans Firestore
                                if (isExpired) {
                                    Log.d("Animation", "Animation expired, marking as inactive")
                                    try {
                                        document.reference.update("status", "inactive")
                                    } catch (e: Exception) {
                                        Log.e("Animation", "Error updating expired animation: ${e.message}")
                                    }
                                    continue
                                }
                                
                                // Vérifier si c'est la plus récente pour ce type d'événement
                                val createdAtTimestamp = data["createdAt"] as? com.google.firebase.Timestamp
                                val timestamp = createdAtTimestamp?.toDate()?.time ?: 0
                                
                                if (timestamp > mostRecentTimestamp) {
                                    mostRecentTimestamp = timestamp
                                    mostRecentAnimation = ScheduledAnimation(
                                        animationType = data["animationType"] as? String ?: "",
                                        eventType = configEventType,
                                        startTime = startTime,
                                        endTime = endTime,
                                        isActive = configStatus == "active",
                                        isExpired = isExpired
                                    )
                                }
                            } else {
                                Log.d("Animation", "Event types don't match. Config: $configEventType, User: $eventType")
                            }
                        }
                    }
                    
                    if (mostRecentAnimation != null) {
                        Log.d("Animation", "Returning most recent animation: ${mostRecentAnimation.animationType}")
                    } else {
                        Log.d("Animation", "No matching animation found in Firestore")
                    }
                    
                    return@withContext mostRecentAnimation
                } catch (e: Exception) {
                    Log.e("Animation", "Error querying Firestore: ${e.message}", e)
                    null
                }
            }
        }

        // Fonction helper pour parser la configuration d'animation
        fun parseAnimationConfig(jsonObject: JSONObject): AnimationConfig {
            val animationDataJson = jsonObject.getJSONObject("animationData")
            val usersJson = animationDataJson.getJSONObject("users")
            
            val users = mutableMapOf<String, LegacyAnimationUser>()
            usersJson.keys().forEach { key ->
                val userJson = usersJson.getJSONObject(key)
                val framesArray = userJson.getJSONArray("frames")
                val frames = mutableListOf<String>()
                for (i in 0 until framesArray.length()) {
                    frames.add(framesArray.getString(i))
                }
                users[key] = LegacyAnimationUser(frames)
            }

            val animationData = AnimationData(
                animationId = animationDataJson.getString("animationId"),
                frameRate = animationDataJson.getInt("frameRate"),
                frameCount = animationDataJson.getInt("frameCount"),
                users = users
            )

            return AnimationConfig(
                animationStartTime = jsonObject.getString("animationStartTime"),
                eventType = jsonObject.getString("eventType"),
                animationType = jsonObject.getString("animationType"),
                animationData = animationData,
                status = jsonObject.getString("status")
            )
        }
        
        // ===================================================================================
        // NEW SYNCHRONIZED ANIMATION SYSTEM
        // ===================================================================================
        
        /**
         * Get event type for animation based on user selection
         */
        private fun getEventTypeForAnimation(eventName: String): String {
            return when (eventName) {
                "Stade de foot" -> "football_stadium"
                "Théâtre" -> "theater"
                "Salle de concert" -> "concert_hall"
                "Salle de spectacle" -> "arena"
                else -> "general"
            }
        }
        
        /**
         * Calculate end time for an animation
         */
        private fun calculateEndTime(startTime: String, frameCount: Int, frameRate: Int): String {
            return try {
                val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
                val startTimeFormatted = if (startTime.contains("T") && startTime.length <= 16) {
                    startTime + ":00"
                } else if (startTime.endsWith("Z")) {
                    startTime.replace("Z", "")
                } else {
                    startTime
                }
                
                val startDate = dateFormat.parse(startTimeFormatted)
                val durationSeconds = frameCount.toDouble() / frameRate.toDouble()
                
                val calendar = Calendar.getInstance()
                calendar.time = startDate
                calendar.add(Calendar.SECOND, durationSeconds.toInt())
                
                dateFormat.format(calendar.time)
            } catch (e: Exception) {
                Log.e("Animation", "Error calculating end time: ${e.message}")
                startTime
            }
        }
        
        /**
         * Check if animation is expired
         */
        private fun isAnimationExpired(endTime: String): Boolean {
            return try {
                val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
                val endDate = dateFormat.parse(endTime)
                val currentDate = Date()
                currentDate.after(endDate)
            } catch (e: Exception) {
                Log.e("Animation", "Error checking expiration: ${e.message}")
                false
            }
        }
        
        /**
         * Get synchronized animation from the new Firebase structure
         * Structure: animations/{animationId}/users/{userId}
         */
        suspend fun getSynchronizedUserAnimation(
            httpClient: OkHttpClient,
            userSeat: UserSeat
        ): UserAnimationPackage? {
            return withContext(Dispatchers.IO) {
                try {
                    val userId = generateUserId(userSeat.row, userSeat.seat)
                    Log.d("Animation", "🔄 SYNC: Getting synchronized animation for user: $userId")
                    
                    // Get active animations for this event type
                    val eventTypeForAnimation = getEventTypeForAnimation(userSeat.event)
                    val activeAnimations = getActiveSynchronizedAnimations(eventTypeForAnimation)
                    
                    if (activeAnimations.isEmpty()) {
                        Log.d("Animation", "No active synchronized animations found")
                        return@withContext null
                    }
                    
                    // Get the most recent animation
                    val mostRecentAnimation = activeAnimations.maxByOrNull { it.createdAt }
                    if (mostRecentAnimation == null) {
                        Log.d("Animation", "No recent animations found")
                        return@withContext null
                    }
                    
                    // Get user-specific animation data
                    val userAnimationData = getUserAnimationData(mostRecentAnimation.animationId, userId)
                        ?: return@withContext null.also { 
                            Log.d("Animation", "No user animation data found for $userId") 
                        }
                    
                    // Calculate end time
                    val endTime = calculateEndTime(
                        userAnimationData.startTime,
                        userAnimationData.frameCount,
                        userAnimationData.frameRate
                    )
                    
                    // Check if animation is expired
                    val isExpired = isAnimationExpired(endTime)
                    
                    val animationPackage = UserAnimationPackage(
                        userId = userId,
                        animationType = userAnimationData.animationType,
                        eventType = eventTypeForAnimation,
                        startTime = userAnimationData.startTime,
                        endTime = endTime,
                        frames = userAnimationData.frames,
                        frameRate = userAnimationData.frameRate,
                        frameCount = userAnimationData.frameCount,
                        isActive = mostRecentAnimation.active && !isExpired,
                        isExpired = isExpired,
                        animationId = mostRecentAnimation.animationId,
                        duration = mostRecentAnimation.duration,
                        pattern = mostRecentAnimation.pattern,
                        createdAt = userAnimationData.createdAt
                    )
                    
                    Log.d("Animation", "✅ SYNC: Successfully created animation package with ${animationPackage.frames.size} frames")
                    return@withContext animationPackage
                    
                } catch (e: Exception) {
                    Log.e("Animation", "💥 SYNC ERROR: ${e.message}", e)
                    return@withContext null
                }
            }
        }
        
        /**
         * Get all active synchronized animations for an event type
         */
        private suspend fun getActiveSynchronizedAnimations(eventType: String): List<SynchronizedAnimation> {
            return try {
                val db = FirebaseFirestore.getInstance()
                val animationsRef = db.collection("animations")
                    .whereEqualTo("eventType", eventType)
                    .whereEqualTo("active", true)
                
                val snapshot = animationsRef.get().await()
                val animations = mutableListOf<SynchronizedAnimation>()
                
                snapshot.documents.forEach { doc ->
                    try {
                        val animation = SynchronizedAnimation(
                            animationId = doc.id,
                            animationType = doc.getString("animationType") ?: "",
                            eventType = doc.getString("eventType") ?: "",
                            startTime = doc.getString("startTime") ?: "",
                            frameRate = doc.getLong("frameRate")?.toInt() ?: 15,
                            frameCount = doc.getLong("frameCount")?.toInt() ?: 80,
                            duration = doc.getDouble("duration") ?: 5.0,
                            active = doc.getBoolean("active") ?: false,
                            createdAt = doc.getString("createdAt") ?: "",
                            updatedAt = doc.getString("updatedAt") ?: "",
                            totalUsers = doc.getLong("totalUsers")?.toInt() ?: 0,
                            pattern = doc.getString("pattern") ?: ""
                        )
                        animations.add(animation)
                    } catch (e: Exception) {
                        Log.e("Animation", "Error parsing animation document: ${e.message}")
                    }
                }
                
                Log.d("Animation", "Found ${animations.size} active synchronized animations")
                animations
                
            } catch (e: Exception) {
                Log.e("Animation", "Error getting active synchronized animations: ${e.message}")
                emptyList()
            }
        }
        
        /**
         * Get user-specific animation data from Firebase
         */
        private suspend fun getUserAnimationData(animationId: String, userId: String): AnimationUser? {
            return try {
                val db = FirebaseFirestore.getInstance()
                val userRef = db.collection("animations")
                    .document(animationId)
                    .collection("users")
                    .document(userId)
                
                val snapshot = userRef.get().await()
                
                if (!snapshot.exists()) {
                    Log.d("Animation", "No user animation data found for $userId in $animationId")
                    return null
                }
                
                val frames = snapshot.get("frames") as? List<String> ?: emptyList()
                
                AnimationUser(
                    userId = snapshot.getString("userId") ?: userId,
                    animationId = snapshot.getString("animationId") ?: animationId,
                    animationType = snapshot.getString("animationType") ?: "",
                    frames = frames,
                    startTime = snapshot.getString("startTime") ?: "",
                    frameRate = snapshot.getLong("frameRate")?.toInt() ?: 15,
                    frameCount = snapshot.getLong("frameCount")?.toInt() ?: frames.size,
                    createdAt = snapshot.getString("createdAt") ?: ""
                )
                
            } catch (e: Exception) {
                Log.e("Animation", "Error getting user animation data: ${e.message}")
                null
            }
        }
        
        /**
         * Function to load animation frames without playing them
         */
        fun loadAnimationFrames(
            animationId: String,
            row: Int,
            col: Int,
            onFramesLoaded: (String, List<ColorFrame>) -> Unit,
            onFramesError: (String) -> Unit
        ): com.google.firebase.firestore.ListenerRegistration? {
            val db = FirebaseFirestore.getInstance()
            val userId = "user_${row}_${col}"
            
            Log.d("Animation", "📦 Loading animation frames: $animationId for user: $userId")
            
            // Listen for animation document changes
            return db.collection("animations")
                .document(animationId)
                .addSnapshotListener { documentSnapshot, error ->
                    if (error != null) {
                        Log.e("Animation", "Error listening to animation: ${error.message}")
                        onFramesError("Erreur de connexion: ${error.message}")
                        return@addSnapshotListener
                    }
                    
                    if (documentSnapshot != null && documentSnapshot.exists()) {
                        val animationData = documentSnapshot.data
                        if (animationData != null) {
                            val animationType = animationData["type"] as? String ?: ""
                            
                            if (animationType == "color_animation") {
                                // Load user color data without playing
                                loadUserColorFrames(animationId, userId, onFramesLoaded, onFramesError)
                            } else {
                                onFramesError("Type d'animation non supporté: $animationType")
                            }
                        }
                    } else {
                        Log.d("Animation", "Animation document not found: $animationId")
                        onFramesError("Animation non trouvée: $animationId")
                    }
                }
        }
        
        /**
         * Function to load and play color animations (scheduled)
         */
        fun loadAndPlayAnimation(
            animationId: String,
            row: Int,
            col: Int,
            onAnimationLoaded: (String, Int) -> Unit,
            onAnimationStart: (String) -> Unit,
            onAnimationFrame: (Int, ColorFrame) -> Unit,
            onAnimationEnd: (String) -> Unit,
            onAnimationError: (String) -> Unit
        ): com.google.firebase.firestore.ListenerRegistration? {
            val db = FirebaseFirestore.getInstance()
            val userId = "user_${row}_${col}"
            
            Log.d("Animation", "🎨 Loading color animation: $animationId for user: $userId")
            
            // Listen for animation document changes
            return db.collection("animations")
                .document(animationId)
                .addSnapshotListener { documentSnapshot, error ->
                    if (error != null) {
                        Log.e("Animation", "Error listening to animation: ${error.message}")
                        onAnimationError("Erreur de connexion: ${error.message}")
                        return@addSnapshotListener
                    }
                    
                    if (documentSnapshot != null && documentSnapshot.exists()) {
                        val animationData = documentSnapshot.data
                        if (animationData != null) {
                            val frameRate = (animationData["frameRate"] as? Number)?.toInt() ?: 2
                            val frameCount = (animationData["frameCount"] as? Number)?.toInt() ?: 20
                            val startTime = animationData["startTime"] as? String ?: ""
                            val animationType = animationData["type"] as? String ?: ""
                            
                            Log.d("Animation", "🎨 Animation data loaded: frameRate=$frameRate, frameCount=$frameCount, type=$animationType")
                            
                            if (animationType == "color_animation") {
                                // Load user color data
                                loadUserColorData(
                                    animationId, userId, frameRate, frameCount, startTime,
                                    onAnimationLoaded, onAnimationStart, onAnimationFrame, onAnimationEnd, onAnimationError
                                )
                            } else {
                                onAnimationError("Type d'animation non supporté: $animationType")
                            }
                        }
                    } else {
                        Log.d("Animation", "Animation document not found: $animationId")
                        onAnimationError("Animation non trouvée: $animationId")
                    }
                }
        }
        
        /**
         * Load user-specific color frames without playing animation
         */
        private fun loadUserColorFrames(
            animationId: String,
            userId: String,
            onFramesLoaded: (String, List<ColorFrame>) -> Unit,
            onFramesError: (String) -> Unit
        ) {
            val db = FirebaseFirestore.getInstance()
            
            Log.d("Animation", "📦 Loading user color frames for: $userId")
            
            db.collection("animations")
                .document(animationId)
                .collection("users")
                .document(userId)
                .get()
                .addOnSuccessListener { userDocument ->
                    if (userDocument.exists()) {
                        val userData = userDocument.data
                        if (userData != null) {
                            val colorsData = userData["colors"] as? List<Map<String, Any>>
                            if (colorsData != null) {
                                val colors = colorsData.map { colorMap ->
                                    ColorFrame(
                                        r = (colorMap["r"] as? Number)?.toInt() ?: 0,
                                        g = (colorMap["g"] as? Number)?.toInt() ?: 0,
                                        b = (colorMap["b"] as? Number)?.toInt() ?: 0
                                    )
                                }
                                
                                Log.d("Animation", "📦 User color frames loaded: ${colors.size} colors")
                                onFramesLoaded(animationId, colors)
                            } else {
                                onFramesError("Données de couleur manquantes pour l'utilisateur $userId")
                            }
                        }
                    } else {
                        onFramesError("Utilisateur non trouvé: $userId")
                    }
                }
                .addOnFailureListener { exception ->
                    Log.e("Animation", "Error loading user frames: ${exception.message}")
                    onFramesError("Erreur de chargement: ${exception.message}")
                }
        }
        
        /**
         * Load user-specific color data and schedule animation
         */
        private fun loadUserColorData(
            animationId: String,
            userId: String,
            frameRate: Int,
            frameCount: Int,
            startTime: String,
            onAnimationLoaded: (String, Int) -> Unit,
            onAnimationStart: (String) -> Unit,
            onAnimationFrame: (Int, ColorFrame) -> Unit,
            onAnimationEnd: (String) -> Unit,
            onAnimationError: (String) -> Unit
        ) {
            val db = FirebaseFirestore.getInstance()
            
            Log.d("Animation", "🎨 Loading user color data for: $userId")
            
            db.collection("animations")
                .document(animationId)
                .collection("users")
                .document(userId)
                .get()
                .addOnSuccessListener { userDocument ->
                    if (userDocument.exists()) {
                        val userData = userDocument.data
                        if (userData != null) {
                            val colorsData = userData["colors"] as? List<Map<String, Any>>
                            if (colorsData != null) {
                                val colors = colorsData.map { colorMap ->
                                    ColorFrame(
                                        r = (colorMap["r"] as? Number)?.toInt() ?: 0,
                                        g = (colorMap["g"] as? Number)?.toInt() ?: 0,
                                        b = (colorMap["b"] as? Number)?.toInt() ?: 0
                                    )
                                }
                                
                                Log.d("Animation", "🎨 User colors loaded: ${colors.size} colors")
                                onAnimationLoaded(animationId, colors.size)
                                
                                // Schedule animation
                                scheduleColorAnimation(animationId, colors, frameRate, startTime, onAnimationStart, onAnimationFrame, onAnimationEnd, onAnimationError)
                            } else {
                                onAnimationError("Données de couleur manquantes pour l'utilisateur $userId")
                            }
                        }
                    } else {
                        onAnimationError("Utilisateur non trouvé: $userId")
                    }
                }
                .addOnFailureListener { exception ->
                    Log.e("Animation", "Error loading user data: ${exception.message}")
                    onAnimationError("Erreur de chargement: ${exception.message}")
                }
        }
        
        /**
         * Schedule color animation according to startTime
         */
        private fun scheduleColorAnimation(
            animationId: String,
            colors: List<ColorFrame>,
            frameRate: Int,
            startTime: String,
            onAnimationStart: (String) -> Unit,
            onAnimationFrame: (Int, ColorFrame) -> Unit,
            onAnimationEnd: (String) -> Unit,
            onAnimationError: (String) -> Unit
        ) {
            try {
                // Parse startTime - handle multiple formats
                val startDate = try {
                    when {
                        startTime.endsWith("Z") -> {
                            // Try full format with Z first
                            try {
                                SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.getDefault()).parse(startTime)
                            } catch (e: Exception) {
                                // Try without seconds
                                SimpleDateFormat("yyyy-MM-dd'T'HH:mm'Z'", Locale.getDefault()).parse(startTime)
                            }
                        }
                        startTime.contains("T") -> {
                            // Try format without Z
                            try {
                                SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault()).parse(startTime)
                            } catch (e: Exception) {
                                // Try without seconds (datetime-local format)
                                SimpleDateFormat("yyyy-MM-dd'T'HH:mm", Locale.getDefault()).parse(startTime)
                            }
                        }
                        else -> {
                            Log.e("Animation", "Unknown date format: $startTime")
                            null
                        }
                    }
                } catch (e: Exception) {
                    Log.e("Animation", "Failed to parse start time: $startTime", e)
                    null
                }
                
                val currentDate = Date()
                
                if (startDate == null) {
                    Log.e("Animation", "Invalid start time format: $startTime")
                    onAnimationError("Format d'heure invalide: $startTime")
                    return
                }
                
                val delayMs = startDate.time - currentDate.time
                
                if (delayMs > 0) {
                    Log.d("Animation", "🎨 Scheduling color animation to start in ${delayMs}ms")
                    android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
                        playColorAnimation(animationId, colors, frameRate, onAnimationStart, onAnimationFrame, onAnimationEnd)
                    }, delayMs)
                } else {
                    Log.d("Animation", "🎨 Start time has passed, waiting for next scheduled start time")
                    // Don't play immediately - animation should only start at scheduled time
                    // Frames are loaded but animation waits for proper start time
                }
                
            } catch (e: Exception) {
                Log.e("Animation", "Error scheduling color animation: ${e.message}")
                onAnimationError("Erreur de planification: ${e.message}")
            }
        }
        
        /**
         * Play color animation
         */
        private fun playColorAnimation(
            animationId: String,
            colors: List<ColorFrame>,
            frameRate: Int,
            onAnimationStart: (String) -> Unit,
            onAnimationFrame: (Int, ColorFrame) -> Unit,
            onAnimationEnd: (String) -> Unit
        ) {
            onAnimationStart(animationId)
            
            val frameDurationMs = (1000.0 / frameRate).toLong()
            var currentFrame = 0
            val handler = android.os.Handler(android.os.Looper.getMainLooper())
            
            Log.d("Animation", "🎨 Starting color animation: $animationId with ${colors.size} colors at ${frameRate}fps")
            
            val playNextFrame = object : Runnable {
                override fun run() {
                    if (currentFrame < colors.size) {
                        val color = colors[currentFrame]
                        Log.d("Animation", "🎨 Playing color frame $currentFrame: RGB(${color.r}, ${color.g}, ${color.b})")
                        
                        onAnimationFrame(currentFrame, color)
                        currentFrame++
                        
                        handler.postDelayed(this, frameDurationMs)
                    } else {
                        Log.d("Animation", "🎨 Color animation finished: $animationId")
                        onAnimationEnd(animationId)
                    }
                }
            }
            
            playNextFrame.run()
        }

        /**
         * Listen for real-time animation updates
         */
        fun listenForAnimationUpdates(
            eventType: String,
            userId: String,
            onAnimationUpdate: (UserAnimationPackage?) -> Unit
        ): com.google.firebase.firestore.ListenerRegistration {
            val db = FirebaseFirestore.getInstance()
            
            // Listen for changes in animations collection
            return db.collection("animations")
                .whereEqualTo("eventType", eventType)
                .whereEqualTo("active", true)
                .addSnapshotListener { snapshot, error ->
                    if (error != null) {
                        Log.e("Animation", "Error listening for animation updates: ${error.message}")
                        return@addSnapshotListener
                    }
                    
                    if (snapshot != null && !snapshot.isEmpty) {
                        // Get the most recent animation
                        val mostRecentDoc = snapshot.documents.maxByOrNull { 
                            it.getString("createdAt") ?: "" 
                        }
                        
                        if (mostRecentDoc != null) {
                            val animationId = mostRecentDoc.id
                            
                            // Listen for user-specific data within this animation
                            db.collection("animations")
                                .document(animationId)
                                .collection("users")
                                .document(userId)
                                .addSnapshotListener { userSnapshot, userError ->
                                    if (userError != null) {
                                        Log.e("Animation", "Error listening for user animation: ${userError.message}")
                                        return@addSnapshotListener
                                    }
                                    
                                    if (userSnapshot != null && userSnapshot.exists()) {
                                        // Build UserAnimationPackage from the data
                                        try {
                                            val frames = userSnapshot.get("frames") as? List<String> ?: emptyList()
                                            val startTime = userSnapshot.getString("startTime") ?: ""
                                            val frameRate = userSnapshot.getLong("frameRate")?.toInt() ?: 15
                                            val frameCount = userSnapshot.getLong("frameCount")?.toInt() ?: frames.size
                                            
                                            val endTime = calculateEndTime(startTime, frameCount, frameRate)
                                            val isExpired = isAnimationExpired(endTime)
                                            
                                            val animationPackage = UserAnimationPackage(
                                                userId = userId,
                                                animationType = userSnapshot.getString("animationType") ?: "",
                                                eventType = eventType,
                                                startTime = startTime,
                                                endTime = endTime,
                                                frames = frames,
                                                frameRate = frameRate,
                                                frameCount = frameCount,
                                                isActive = !isExpired,
                                                isExpired = isExpired,
                                                animationId = animationId,
                                                duration = mostRecentDoc.getDouble("duration") ?: 5.0,
                                                pattern = mostRecentDoc.getString("pattern") ?: "",
                                                createdAt = userSnapshot.getString("createdAt") ?: ""
                                            )
                                            
                                            onAnimationUpdate(animationPackage)
                                        } catch (e: Exception) {
                                            Log.e("Animation", "Error building animation package: ${e.message}")
                                            onAnimationUpdate(null)
                                        }
                                    } else {
                                        onAnimationUpdate(null)
                                    }
                                }
                        }
                    } else {
                        onAnimationUpdate(null)
                    }
                }
        }
        
        /**
         * Schedule animation playback at the specified start time
         */
        fun scheduleAnimationPlayback(
            animationPackage: UserAnimationPackage,
            onAnimationStart: () -> Unit,
            onAnimationFrame: (String) -> Unit,
            onAnimationEnd: () -> Unit
        ) {
            try {
                val startTime = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
                    .parse(animationPackage.startTime.replace("Z", ""))
                val currentTime = Date()
                
                if (startTime == null) {
                    Log.e("Animation", "Invalid start time format: ${animationPackage.startTime}")
                    return
                }
                
                val delayMs = startTime.time - currentTime.time
                
                if (delayMs > 0) {
                    Log.d("Animation", "Scheduling animation to start in ${delayMs}ms")
                    android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
                        playAnimationFrames(animationPackage, onAnimationStart, onAnimationFrame, onAnimationEnd)
                    }, delayMs)
                } else {
                    Log.d("Animation", "Animation start time has passed, waiting for next scheduled start time")
                    // Don't play immediately - animation should only start at scheduled time
                    // Frames are loaded but animation waits for proper start time
                }
                
            } catch (e: Exception) {
                Log.e("Animation", "Error scheduling animation playback: ${e.message}")
            }
        }
        
        /**
         * Play animation frames in sequence
         */
        private fun playAnimationFrames(
            animationPackage: UserAnimationPackage,
            onAnimationStart: () -> Unit,
            onAnimationFrame: (String) -> Unit,
            onAnimationEnd: () -> Unit
        ) {
            Log.d("Animation", "🎬 Starting animation playback: ${animationPackage.animationType}")
            onAnimationStart()
            
            val frameDurationMs = (1000.0 / animationPackage.frameRate).toLong()
            val handler = android.os.Handler(android.os.Looper.getMainLooper())
            
            var currentFrame = 0
            
            val playNextFrame = object : Runnable {
                override fun run() {
                    if (currentFrame < animationPackage.frames.size) {
                        val frameUrl = animationPackage.frames[currentFrame]
                        Log.d("Animation", "Playing frame ${currentFrame + 1}/${animationPackage.frames.size}: $frameUrl")
                        onAnimationFrame(frameUrl)
                        currentFrame++
                        handler.postDelayed(this, frameDurationMs)
                    } else {
                        Log.d("Animation", "🎬 Animation finished")
                        onAnimationEnd()
                    }
                }
            }
            
            playNextFrame.run()
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(
    events: List<Event>, 
    auth: FirebaseAuth, 
    db: FirebaseFirestore, 
    httpClient: OkHttpClient,
    context: Context
) {
    var selectedEvent by remember { mutableStateOf<Event?>(null) }
    var selectedStand by remember { mutableStateOf<String?>(null) }
    var selectedRow by remember { mutableStateOf<Int?>(null) }
    var selectedSeat by remember { mutableStateOf<Int?>(null) }

    var isLoading by remember { mutableStateOf(false) }
    var activeAnimationConfig by remember { mutableStateOf<AnimationConfig?>(null) }
    var animationStatus by remember { mutableStateOf("Aucune animation active") }
    var currentUserSeat by remember { mutableStateOf<UserSeat?>(null) }
    var isInWaitingRoom by remember { mutableStateOf(false) }
    var scheduledAnimation by remember { mutableStateOf<ScheduledAnimation?>(null) }
    val coroutineScope = rememberCoroutineScope()

    // État pour suivre l'étape actuelle de la sélection
    var currentStep by remember { mutableStateOf(1) }

    // Charger la configuration d'animation active au démarrage
    LaunchedEffect(Unit) {
        try {
            activeAnimationConfig = MainActivity.getActiveAnimationConfig(httpClient)
            animationStatus = if (activeAnimationConfig != null) {
                "Animation active: ${activeAnimationConfig?.animationType}"
            } else {
                "Aucune animation active"
            }
        } catch (e: Exception) {
            Log.e("Animation", "Error loading animation config: ${e.message}")
            animationStatus = "Erreur de chargement d'animation"
        }
    }

    if (isLoading) {
        LoadingScreen()
    } else if (isInWaitingRoom && currentUserSeat != null) {
        WaitingRoomScreen(
            userSeat = currentUserSeat!!,
            scheduledAnimation = scheduledAnimation,
            onBackToSeatSelection = {
                isInWaitingRoom = false
                currentUserSeat = null
                scheduledAnimation = null
                currentStep = 1
                selectedEvent = null
                selectedStand = null
                selectedRow = null
                selectedSeat = null
            }
        )
    } else {
        StepBasedSeatSelection(
            events = events,
            currentStep = currentStep,
            selectedEvent = selectedEvent,
            selectedStand = selectedStand,
            selectedRow = selectedRow,
            selectedSeat = selectedSeat,
            onEventSelected = { event ->
                selectedEvent = event
                selectedStand = null
                selectedRow = null
                selectedSeat = null
            },
            onStandSelected = { stand ->
                selectedStand = stand
            },
            onRowSelected = { row ->
                selectedRow = row
            },
            onSeatSelected = { seat ->
                selectedSeat = seat
            },
            onNextStep = { currentStep++ },
            onPreviousStep = { currentStep-- },
            onValidate = {
                isLoading = true
                coroutineScope.launch {
                    try {
                        Log.d("Firebase", "Début de la sauvegarde...")
                        
                        // Authentification anonyme
                        val authResult = auth.signInAnonymously().await()
                        val userId = authResult.user?.uid ?: ""
                        Log.d("Firebase", "Authentification réussie, userId: $userId")
                        
                        // Préparer les données à sauvegarder
                        val seatSelection = hashMapOf(
                            "evenement" to (selectedEvent?.name ?: ""),
                            "tribune" to (selectedStand ?: ""),
                            "rang" to (selectedRow ?: 0),
                            "numeroDePlace" to (selectedSeat ?: 0),
                            "timestamp" to Timestamp.now(),
                            "userId" to userId
                        )
                        
                        Log.d("Firebase", "Données préparées: $seatSelection")
                        
                        // Sauvegarder dans Firestore
                        val documentRef = db.collection("seat_selections")
                            .add(seatSelection)
                            .await()
                        
                        Log.d("Firebase", "Sélection sauvegardée avec succès! ID: ${documentRef.id}")
                        
                        // Créer l'objet UserSeat
                        currentUserSeat = UserSeat(
                            event = selectedEvent?.name ?: "",
                            stand = selectedStand ?: "",
                            row = selectedRow ?: 0,
                            seat = selectedSeat ?: 0,
                            userId = userId
                        )
                        
                        // Vérifier s'il y a des animations programmées pour cet événement
                        val eventTypeForAnimation = when (selectedEvent?.name) {
                            "Stade de foot" -> "football_stadium"
                            "Salle de concert" -> "concert_hall"
                            "Théâtre" -> "theater"
                            else -> "general"
                        }
                        
                        scheduledAnimation = MainActivity.checkScheduledAnimations(httpClient, eventTypeForAnimation)
                        
                        // Naviguer vers la salle d'attente
                        isInWaitingRoom = true
                        
                        Toast.makeText(context, "Sélection sauvegardée! Bienvenue dans la salle d'attente.", Toast.LENGTH_SHORT).show()
                        
                    } catch (e: Exception) {
                        Log.e("Firebase", "Erreur lors de la sauvegarde: ${e.message}", e)
                        Toast.makeText(context, "Erreur: ${e.message}", Toast.LENGTH_LONG).show()
                    } finally {
                        isLoading = false
                    }
                }
            }
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StepBasedSeatSelection(
    events: List<Event>,
    currentStep: Int,
    selectedEvent: Event?,
    selectedStand: String?,
    selectedRow: Int?,
    selectedSeat: Int?,
    onEventSelected: (Event) -> Unit,
    onStandSelected: (String) -> Unit,
    onRowSelected: (Int) -> Unit,
    onSeatSelected: (Int) -> Unit,
    onNextStep: () -> Unit,
    onPreviousStep: () -> Unit,
    onValidate: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Titre principal
        Text(
            text = "Sélection de place",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold
        )
        
        // Indicateur d'étape
        Text(
            text = "Étape $currentStep sur 3",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        // Affichage des informations sélectionnées (étapes 2 et 3)
        if (currentStep >= 2) {
            SelectedInfoDisplay(
                selectedEvent = selectedEvent,
                selectedStand = selectedStand,
                selectedRow = selectedRow,
                selectedSeat = selectedSeat,
                currentStep = currentStep
            )
        }
        
        // Contenu principal selon l'étape
        when (currentStep) {
            1 -> EventSelectionStep(
                events = events,
                selectedEvent = selectedEvent,
                onEventSelected = onEventSelected,
                onNextStep = onNextStep
            )
            2 -> TribuneSelectionStep(
                event = selectedEvent,
                selectedStand = selectedStand,
                onStandSelected = onStandSelected,
                onNextStep = onNextStep,
                onPreviousStep = onPreviousStep
            )
            3 -> RowSeatInputStep(
                selectedRow = selectedRow,
                selectedSeat = selectedSeat,
                onRowSelected = onRowSelected,
                onSeatSelected = onSeatSelected
            )
        }
        
        Spacer(modifier = Modifier.weight(1f))
        
        // Boutons de navigation (seulement pour l'étape 3)
        if (currentStep == 3) {
            NavigationButtons(
                currentStep = currentStep,
                selectedEvent = selectedEvent,
                selectedStand = selectedStand,
                selectedRow = selectedRow,
                selectedSeat = selectedSeat,
                onNextStep = onNextStep,
                onPreviousStep = onPreviousStep,
                onValidate = onValidate
            )
        }
    }
}

@Composable
fun SelectedInfoDisplay(
    selectedEvent: Event?,
    selectedStand: String?,
    selectedRow: Int?,
    selectedSeat: Int?,
    currentStep: Int
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Sélection en cours",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // Événement (toujours affiché à partir de l'étape 2)
            if (selectedEvent != null) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "Événement:",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = selectedEvent.name,
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
            
            // Tribune (affiché à partir de l'étape 3)
            if (currentStep >= 3 && selectedStand != null) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "Tribune:",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = selectedStand,
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
        }
    }
}

@Composable
fun EventSelectionStep(
    events: List<Event>,
    selectedEvent: Event?,
    onEventSelected: (Event) -> Unit,
    onNextStep: () -> Unit
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = "Sélectionnez votre événement",
            style = MaterialTheme.typography.titleMedium,
            textAlign = TextAlign.Center
        )
        
        EventDropdown(
            events = events,
            selectedEvent = selectedEvent,
            onEventSelected = onEventSelected
        )
        
        Button(
            onClick = onNextStep,
            enabled = selectedEvent != null,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Continuer")
        }
    }
}

@Composable
fun TribuneSelectionStep(
    event: Event?,
    selectedStand: String?,
    onStandSelected: (String) -> Unit,
    onNextStep: () -> Unit,
    onPreviousStep: () -> Unit
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = "Sélectionnez votre tribune",
            style = MaterialTheme.typography.titleMedium,
            textAlign = TextAlign.Center
        )
        
        if (event != null) {
            StandDropdown(
                stands = event.stands,
                selectedStand = selectedStand,
                onStandSelected = onStandSelected
            )
        }
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            OutlinedButton(
                onClick = onPreviousStep,
                modifier = Modifier.weight(1f)
            ) {
                Text("Retour")
            }
            
            Button(
                onClick = onNextStep,
                enabled = selectedStand != null,
                modifier = Modifier.weight(1f)
            ) {
                Text("Continuer")
            }
        }
    }
}

@Composable
fun RowSeatInputStep(
    selectedRow: Int?,
    selectedSeat: Int?,
    onRowSelected: (Int) -> Unit,
    onSeatSelected: (Int) -> Unit
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(24.dp)
    ) {
        Text(
            text = "Saisissez votre place",
            style = MaterialTheme.typography.titleMedium,
            textAlign = TextAlign.Center
        )
        
        
        // Clavier numérique
        NumericKeypad(
            onRowSelected = onRowSelected,
            onSeatSelected = onSeatSelected,
            selectedRow = selectedRow,
            selectedSeat = selectedSeat,
            onRowCardClick = { /* Switch to row input */ },
            onSeatCardClick = { /* Switch to seat input */ }
        )
    }
}

@Composable
fun NumericKeypad(
    onRowSelected: (Int) -> Unit,
    onSeatSelected: (Int) -> Unit,
    selectedRow: Int?,
    selectedSeat: Int?,
    onRowCardClick: () -> Unit,
    onSeatCardClick: () -> Unit
) {
    var inputMode by remember { mutableStateOf("row") } // "row" ou "seat"
    var currentInput by remember { mutableStateOf("") } // Pour accumuler les chiffres tapés
    
    fun handleDigitClick(digit: String) {
        when (currentInput.length) {
            0 -> {
                // Premier chiffre
                currentInput = digit
            }
            1 -> {
                // Deuxième chiffre - concaténer avec le premier
                val newInput = currentInput + digit
                val value = newInput.toIntOrNull()
                
                if (value != null && value in 1..10) {
                    // Nombre valide, traiter et passer au mode suivant
                    if (inputMode == "row") {
                        onRowSelected(value)
                        inputMode = "seat"
                        currentInput = "" // Réinitialiser pour la saisie du siège
                    } else {
                        onSeatSelected(value)
                        currentInput = "" // Réinitialiser après sélection du siège
                        // Optionnel: rester en mode siège pour permettre de changer
                    }
                } else {
                    // Nombre invalide, recommencer avec le nouveau chiffre
                    currentInput = digit
                }
            }
            else -> {
                // Recommencer avec le nouveau chiffre
                currentInput = digit
            }
        }
    }
    
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Affichage des cartes cliquables
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            Card(
                modifier = Modifier
                    .weight(1f)
                    .clickable { 
                        inputMode = "row"
                        currentInput = ""
                        onRowCardClick()
                    },
                colors = CardDefaults.cardColors(
                    containerColor = if (inputMode == "row") MaterialTheme.colorScheme.primaryContainer
                    else if (selectedRow != null) MaterialTheme.colorScheme.secondaryContainer
                    else MaterialTheme.colorScheme.surface
                ),
                border = if (inputMode == "row") BorderStroke(2.dp, MaterialTheme.colorScheme.primary) else null
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Rang",
                        style = MaterialTheme.typography.labelMedium,
                        color = if (inputMode == "row") MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface
                    )
                    Text(
                        text = if (inputMode == "row" && currentInput.isNotEmpty()) currentInput 
                              else selectedRow?.toString() ?: "?",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        color = if (inputMode == "row") MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface
                    )
                }
            }
            
            Spacer(modifier = Modifier.width(16.dp))
            
            Card(
                modifier = Modifier
                    .weight(1f)
                    .clickable { 
                        inputMode = "seat"
                        currentInput = ""
                        onSeatCardClick()
                    },
                colors = CardDefaults.cardColors(
                    containerColor = if (inputMode == "seat") MaterialTheme.colorScheme.primaryContainer
                    else if (selectedSeat != null) MaterialTheme.colorScheme.secondaryContainer
                    else MaterialTheme.colorScheme.surface
                ),
                border = if (inputMode == "seat") BorderStroke(2.dp, MaterialTheme.colorScheme.primary) else null
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Siège",
                        style = MaterialTheme.typography.labelMedium,
                        color = if (inputMode == "seat") MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface
                    )
                    Text(
                        text = if (inputMode == "seat" && currentInput.isNotEmpty()) currentInput 
                              else selectedSeat?.toString() ?: "?",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        color = if (inputMode == "seat") MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface
                    )
                }
            }
        }
        
        // Affichage du mode et de l'entrée en cours
        Text(
            text = if (inputMode == "row") "Saisissez le rang (01-10)" else "Saisissez le siège (01-10)",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
        )
        
        // Grille de nombres style téléphone
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            // Rangée 7-8-9
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                for (number in 7..9) {
                    PhoneKeypadButton(
                        text = number.toString(),
                        onClick = { handleDigitClick(number.toString()) }
                    )
                }
            }
            
            // Rangée 4-5-6
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                for (number in 4..6) {
                    PhoneKeypadButton(
                        text = number.toString(),
                        onClick = { handleDigitClick(number.toString()) }
                    )
                }
            }
            
            // Rangée 1-2-3
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                for (number in 1..3) {
                    PhoneKeypadButton(
                        text = number.toString(),
                        onClick = { handleDigitClick(number.toString()) }
                    )
                }
            }
            
            // Rangée 0 (seul)
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                PhoneKeypadButton(
                    text = "0",
                    onClick = { handleDigitClick("0") }
                )
            }
        }
    }
}


@Composable
fun PhoneKeypadButton(
    text: String,
    onClick: () -> Unit
) {
    Button(
        onClick = onClick,
        modifier = Modifier.size(64.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = MaterialTheme.colorScheme.outline,
            contentColor = MaterialTheme.colorScheme.onSurface
        ),
        shape = RoundedCornerShape(12.dp)
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
fun NavigationButtons(
    currentStep: Int,
    selectedEvent: Event?,
    selectedStand: String?,
    selectedRow: Int?,
    selectedSeat: Int?,
    onNextStep: () -> Unit,
    onPreviousStep: () -> Unit,
    onValidate: () -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Bouton Retour (sauf à l'étape 1)
        if (currentStep > 1) {
            OutlinedButton(
                onClick = onPreviousStep,
                modifier = Modifier.weight(1f)
            ) {
                Text("Retour")
            }
        }
        
        // Bouton principal
        when (currentStep) {
            1 -> {
                Button(
                    onClick = onNextStep,
                    enabled = selectedEvent != null,
                    modifier = Modifier.weight(if (currentStep > 1) 1f else 1f)
                ) {
                    Text("Continuer")
                }
            }
            2 -> {
                Button(
                    onClick = onNextStep,
                    enabled = selectedStand != null,
                    modifier = Modifier.weight(1f)
                ) {
                    Text("Continuer")
                }
            }
            3 -> {
                Button(
                    onClick = onValidate,
                    enabled = selectedRow != null && selectedSeat != null,
                    modifier = Modifier.weight(1f)
                ) {
                    Text("Valider")
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun EventDropdown(
    events: List<Event>,
    selectedEvent: Event?,
    onEventSelected: (Event) -> Unit
) {
    var expanded by remember { mutableStateOf(false) }

    ExposedDropdownMenuBox(
        expanded = expanded,
        onExpandedChange = { expanded = !expanded }
    ) {
        TextField(
            value = selectedEvent?.name ?: "Sélectionner un événement",
            onValueChange = {}, // Lecture seule
            readOnly = true,
            label = { Text("Événement") },
            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
            modifier = Modifier
                .menuAnchor()
                .fillMaxWidth()
        )
        ExposedDropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false }
        ) {
            events.forEach { event ->
                DropdownMenuItem(
                    text = { Text(event.name) },
                    onClick = {
                        onEventSelected(event)
                        expanded = false
                    }
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StandDropdown(
    stands: List<String>,
    selectedStand: String?,
    onStandSelected: (String) -> Unit
) {
    var expanded by remember { mutableStateOf(false) }

    ExposedDropdownMenuBox(
        expanded = expanded,
        onExpandedChange = { expanded = !expanded }
    ) {
        TextField(
            value = selectedStand ?: "Sélectionner une tribune",
            onValueChange = {}, // Lecture seule
            readOnly = true,
            label = { Text("Tribune") },
            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
            modifier = Modifier
                .menuAnchor()
                .fillMaxWidth()
        )
        ExposedDropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false }
        ) {
            stands.forEach { stand ->
                DropdownMenuItem(
                    text = { Text(stand) },
                    onClick = {
                        onStandSelected(stand)
                        expanded = false
                    }
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NumberDropdown(
    label: String,
    range: IntRange,
    selectedValue: Int?,
    onValueSelected: (Int) -> Unit
) {
    var expanded by remember { mutableStateOf(false) }

    ExposedDropdownMenuBox(
        expanded = expanded,
        onExpandedChange = { expanded = !expanded }
    ) {
        TextField(
            value = selectedValue?.toString() ?: "Sélectionner $label",
            onValueChange = {}, // Lecture seule
            readOnly = true,
            label = { Text(label) },
            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
            modifier = Modifier
                .menuAnchor()
                .fillMaxWidth()
        )
        ExposedDropdownMenu(
            expanded = expanded,
            onDismissRequest = { expanded = false }
        ) {
            range.forEach { number ->
                DropdownMenuItem(
                    text = { Text(number.toString()) },
                    onClick = {
                        onValueSelected(number)
                        expanded = false
                    }
                )
            }
        }
    }
}

@Composable
fun LoadingScreen() {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            CircularProgressIndicator()
            Spacer(modifier = Modifier.height(16.dp))
            Text("Veuillez patienter…")
        }
    }
}

@Composable
fun ColorAnimationView(
    animationId: String,
    row: Int,
    col: Int,
    modifier: Modifier = Modifier,
    onFullScreenChange: (Boolean) -> Unit = {}
) {
    var currentColor by remember { mutableStateOf(Color.Black) }
    var animationStatus by remember { mutableStateOf("Chargement des frames...") }
    var isAnimationActive by remember { mutableStateOf(false) }
    var isFullScreen by remember { mutableStateOf(false) }
    var animationFrames by remember { mutableStateOf<List<ColorFrame>?>(null) }
    var framesListener by remember { mutableStateOf<com.google.firebase.firestore.ListenerRegistration?>(null) }
    var scheduledListener by remember { mutableStateOf<com.google.firebase.firestore.ListenerRegistration?>(null) }
    
    // Load animation frames (without playing)
    LaunchedEffect(animationId, row, col) {
        Log.d("ColorAnimationView", "📦 Loading animation frames: $animationId for user_${row}_${col}")
        
        // Clean up previous listener
        framesListener?.remove()
        
        // Load frames only (not play)
        framesListener = MainActivity.loadAnimationFrames(
            animationId = animationId,
            row = row,
            col = col,
            onFramesLoaded = { id, frames ->
                animationFrames = frames
                animationStatus = "Package reçu"
                Log.d("ColorAnimationView", "📦 Animation frames loaded: $id with ${frames.size} frames")
            },
            onFramesError = { error ->
                animationStatus = "Erreur: $error"
                Log.e("ColorAnimationView", "📦 Animation frames error: $error")
            }
        )
        
        // Listen for scheduled animations
        scheduledListener = MainActivity.loadAndPlayAnimation(
            animationId = animationId,
            row = row,
            col = col,
            onAnimationLoaded = { id, frameCount ->
                Log.d("ColorAnimationView", "🎨 Scheduled animation loaded: $id with $frameCount frames")
            },
            onAnimationStart = { id ->
                animationStatus = "Animation en cours..."
                isAnimationActive = true
                isFullScreen = true
                onFullScreenChange(true)
                Log.d("ColorAnimationView", "🎨 Scheduled animation started: $id")
            },
            onAnimationFrame = { frameIndex, colorFrame ->
                currentColor = androidx.compose.ui.graphics.Color(
                    red = colorFrame.r / 255f,
                    green = colorFrame.g / 255f,
                    blue = colorFrame.b / 255f,
                    alpha = 1f
                )
                Log.d("ColorAnimationView", "🎨 Frame $frameIndex: RGB(${colorFrame.r}, ${colorFrame.g}, ${colorFrame.b})")
            },
            onAnimationEnd = { id ->
                animationStatus = "Animation terminée"
                isAnimationActive = false
                isFullScreen = false
                onFullScreenChange(false)
                Log.d("ColorAnimationView", "🎨 Scheduled animation ended: $id")
            },
            onAnimationError = { error ->
                animationStatus = "Erreur: $error"
                isAnimationActive = false
                isFullScreen = false
                onFullScreenChange(false)
                Log.e("ColorAnimationView", "🎨 Scheduled animation error: $error")
            }
        )
    }
    
    // Cleanup on dispose
    DisposableEffect(animationId, row, col) {
        onDispose {
            Log.d("ColorAnimationView", "🎨 Cleaning up animation listeners")
            framesListener?.remove()
            scheduledListener?.remove()
        }
    }
    
    // UI for color animation
    if (isFullScreen) {
        // Full screen animation mode
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(currentColor),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "🎨",
                color = if (isLightColor(currentColor)) Color.Black else Color.White,
                style = MaterialTheme.typography.displayLarge,
                fontWeight = FontWeight.Bold
            )
        }
    } else {
        // Normal waiting room mode
        Column(
            modifier = modifier,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Color display area
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(300.dp)
                    .background(
                        color = currentColor,
                        shape = RoundedCornerShape(16.dp)
                    )
                    .padding(16.dp),
                contentAlignment = Alignment.Center
            ) {
                if (isAnimationActive) {
                    Text(
                        text = "🎨 Animation en cours",
                        color = if (isLightColor(currentColor)) Color.Black else Color.White,
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold
                    )
                } else {
                    Text(
                        text = "En attente...",
                        color = if (isLightColor(currentColor)) Color.Black else Color.White,
                        style = MaterialTheme.typography.bodyLarge
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Animation status
            Text(
                text = animationStatus,
                style = MaterialTheme.typography.bodyMedium,
                textAlign = TextAlign.Center
            )
            
            // Progress indicator
            if (isAnimationActive) {
                LinearProgressIndicator(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 8.dp),
                    color = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}

@Composable
fun WaitingRoomScreen(
    userSeat: UserSeat,
    scheduledAnimation: ScheduledAnimation?,
    onBackToSeatSelection: () -> Unit
) {
    // Track if animation is in full screen mode
    var isAnimationFullScreen by remember { mutableStateOf(false) }
    
    // Animation state that needs to be tracked at waiting room level
    var animationFrames by remember { mutableStateOf<List<ColorFrame>?>(null) }
    var animationStatus by remember { mutableStateOf("Chargement des frames...") }
    var currentColor by remember { mutableStateOf(Color.Black) }
    var framesListener by remember { mutableStateOf<com.google.firebase.firestore.ListenerRegistration?>(null) }
    var scheduledListener by remember { mutableStateOf<com.google.firebase.firestore.ListenerRegistration?>(null) }
    // État pour l'animation en temps réel
    var currentAnimation by remember { mutableStateOf(scheduledAnimation) }
    var isListening by remember { mutableStateOf(false) }
    var lastUpdateTime by remember { mutableStateOf(System.currentTimeMillis()) }
    
    // État pour le package d'animation utilisateur
    var userAnimationPackage by remember { mutableStateOf<UserAnimationPackage?>(null) }
    var isLoadingPackage by remember { mutableStateOf(false) }
    
    // État pour les notifications de package
    var showPackageNotification by remember { mutableStateOf(false) }
    var packageNotificationMessage by remember { mutableStateOf("") }
    
    // HTTP client pour les requêtes
    val httpClient = remember { OkHttpClient() }
    
    // Déterminer le type d'événement pour le listener
    val eventTypeForAnimation = remember {
        when (userSeat.event) {
            "Stade de foot" -> "football_stadium"
            "Salle de concert" -> "concert_hall"
            "Théâtre" -> "theater"
            else -> "general"
        }
    }
    
    // Fonction pour afficher une notification de package
    fun showPackageNotification(message: String) {
        packageNotificationMessage = message
        showPackageNotification = true
        
        // Masquer la notification après 3 secondes
        kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.Main).launch {
            kotlinx.coroutines.delay(3000)
            showPackageNotification = false
        }
    }
    
    // Fonction pour charger le package d'animation utilisateur
    suspend fun loadUserAnimationPackage() {
        isLoadingPackage = true
        val animationPackage = MainActivity.getUserAnimationPackage(httpClient, userSeat)
        val previousPackage = userAnimationPackage
        userAnimationPackage = animationPackage
        isLoadingPackage = false
        
        if (animationPackage != null) {
            Log.d("Animation", "Loaded animation package for ${animationPackage.userId}: ${animationPackage.frames.size} frames")
            
            // Montrer une notification si c'est un nouveau package ou une mise à jour
            if (previousPackage == null) {
                showPackageNotification("📦 Package couleur reçu (${animationPackage.frames.size} frames)")
            } else if (previousPackage.userId != animationPackage.userId || 
                       previousPackage.animationType != animationPackage.animationType ||
                       previousPackage.frames.size != animationPackage.frames.size) {
                showPackageNotification("🔄 Nouveau package couleur (${animationPackage.frames.size} frames)")
            }
        } else {
            Log.d("Animation", "No animation package available for user")
            if (previousPackage != null) {
                showPackageNotification("📦 Package d'animation supprimé")
            }
        }
    }
    
    // Listener en temps réel pour les changements d'animation avec nettoyage approprié
    DisposableEffect(eventTypeForAnimation) {
        Log.d("Animation", "Setting up real-time listener for event type: $eventTypeForAnimation")
        isListening = true
        
        val db = FirebaseFirestore.getInstance()
        val listener = db.collection("animation_configs")
            .whereEqualTo("status", "active")
            .addSnapshotListener { snapshot, error ->
                if (error != null) {
                    Log.e("Animation", "Error listening for animation changes: ${error.message}")
                    return@addSnapshotListener
                }
                
                if (snapshot != null && !snapshot.isEmpty) {
                    Log.d("Animation", "Received ${snapshot.documents.size} animation updates")
                    
                    // Trouver la plus récente animation pour ce type d'événement
                    var mostRecentAnimation: ScheduledAnimation? = null
                    var mostRecentTimestamp: Long = 0
                    
                    for (document in snapshot.documents) {
                        val data = document.data
                        if (data != null) {
                            val configEventType = data["eventType"] as? String ?: ""
                            
                            if (configEventType == eventTypeForAnimation || configEventType == "all") {
                                // Extraire les données d'animation
                                val animationDataMap = data["animationData"] as? Map<String, Any>
                                val frameCount = (animationDataMap?.get("frameCount") as? Number)?.toInt() ?: 80
                                val frameRate = (animationDataMap?.get("frameRate") as? Number)?.toInt() ?: 15
                                val startTime = data["animationStartTime"] as? String ?: ""
                                
                                // Calculer le temps de fin et vérifier l'expiration
                                val endTime = ScheduledAnimation.calculateEndTime(startTime, frameCount, frameRate)
                                val isExpired = ScheduledAnimation.isAnimationExpired(endTime)
                                
                                if (!isExpired) {
                                    // Vérifier si c'est la plus récente
                                    val createdAtTimestamp = data["createdAt"] as? com.google.firebase.Timestamp
                                    val timestamp = createdAtTimestamp?.toDate()?.time ?: 0
                                    
                                    if (timestamp > mostRecentTimestamp) {
                                        mostRecentTimestamp = timestamp
                                        mostRecentAnimation = ScheduledAnimation(
                                            animationType = data["animationType"] as? String ?: "",
                                            eventType = configEventType,
                                            startTime = startTime,
                                            endTime = endTime,
                                            isActive = true,
                                            isExpired = false
                                        )
                                    }
                                }
                            }
                        }
                    }
                    
                    // Mettre à jour l'animation actuelle
                    if (mostRecentAnimation != currentAnimation) {
                        Log.d("Animation", "Animation updated: ${mostRecentAnimation?.animationType}")
                        currentAnimation = mostRecentAnimation
                        lastUpdateTime = System.currentTimeMillis()
                        
                        // Charger le nouveau package d'animation utilisateur
                        kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.Main).launch {
                            loadUserAnimationPackage()
                        }
                    }
                } else {
                    Log.d("Animation", "No active animations found")
                    if (currentAnimation != null) {
                        currentAnimation = null
                        lastUpdateTime = System.currentTimeMillis()
                        userAnimationPackage = null // Supprimer le package si plus d'animation
                    }
                }
            }
        
        // Fonction de nettoyage pour supprimer le listener
        onDispose {
            Log.d("Animation", "Removing real-time listener")
            listener.remove()
            isListening = false
        }
    }
    
    // Set up animation listeners for any active animation
    LaunchedEffect(userSeat) {
        Log.d("WaitingRoomScreen", "📦 Setting up animation listeners for user_${userSeat.row}_${userSeat.seat}")
        
        // Try to load frames for different animation types
        val animationTypes = listOf("blue_black_flash", "checkboard_flash")
        
        // Try each animation type until we find one with frames
        for (animationType in animationTypes) {
            Log.d("WaitingRoomScreen", "📦 Trying animation type: $animationType")
            
            // Load frames only (not play)
            framesListener = MainActivity.loadAnimationFrames(
                animationId = animationType,
                row = userSeat.row,
                col = userSeat.seat,
                onFramesLoaded = { id, frames ->
                    animationFrames = frames
                    animationStatus = "Package reçu"
                    Log.d("WaitingRoomScreen", "📦 Animation frames loaded: $id with ${frames.size} frames")
                },
                onFramesError = { error ->
                    Log.d("WaitingRoomScreen", "📦 No frames found for $animationType: $error")
                }
            )
            
            // Set up scheduled animation listener for this type
            Log.d("WaitingRoomScreen", "🎨 Setting up scheduled animation listener for $animationType")
            
            scheduledListener = MainActivity.loadAndPlayAnimation(
                animationId = animationType,
                row = userSeat.row,
                col = userSeat.seat,
            onAnimationLoaded = { id, frameCount ->
                Log.d("WaitingRoomScreen", "🎨 Scheduled animation loaded: $id with $frameCount frames")
            },
            onAnimationStart = { id ->
                animationStatus = "Animation en cours..."
                isAnimationFullScreen = true
                Log.d("WaitingRoomScreen", "🎨 Scheduled animation started: $id")
            },
            onAnimationFrame = { frameIndex, colorFrame ->
                currentColor = androidx.compose.ui.graphics.Color(
                    red = colorFrame.r / 255f,
                    green = colorFrame.g / 255f,
                    blue = colorFrame.b / 255f,
                    alpha = 1f
                )
                Log.d("WaitingRoomScreen", "🎨 Frame $frameIndex: RGB(${colorFrame.r}, ${colorFrame.g}, ${colorFrame.b})")
            },
            onAnimationEnd = { id ->
                animationStatus = "Animation terminée"
                isAnimationFullScreen = false
                Log.d("WaitingRoomScreen", "🎨 Scheduled animation ended: $id")
            },
            onAnimationError = { error ->
                animationStatus = "Erreur: $error"
                isAnimationFullScreen = false
                Log.e("WaitingRoomScreen", "🎨 Scheduled animation error: $error")
            }
        )
        }
        
        // Load user animation package
        loadUserAnimationPackage()
    }
    
    // Cleanup listeners on dispose
    DisposableEffect(userSeat) {
        onDispose {
            Log.d("WaitingRoomScreen", "🎨 Cleaning up animation listeners")
            framesListener?.remove()
            scheduledListener?.remove()
        }
    }
    
    Box(modifier = Modifier.fillMaxSize()) {
        if (isAnimationFullScreen) {
            // Full screen animation mode - only show the animation color
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(currentColor)
            )
        } else {
            // Normal waiting room mode
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(24.dp)
            ) {
        // Titre de la salle d'attente
        Text(
            text = "🎭 Salle d'Attente",
            style = MaterialTheme.typography.headlineLarge,
            color = MaterialTheme.colorScheme.primary,
            fontWeight = FontWeight.Bold
        )
        
        // Informations sur la place
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.primaryContainer
            )
        ) {
            Column(
                modifier = Modifier.padding(20.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "🎫 Votre Place",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    text = "Événement: ${userSeat.event}",
                    style = MaterialTheme.typography.bodyLarge
                )
                Text(
                    text = "Tribune: ${userSeat.stand}",
                    style = MaterialTheme.typography.bodyLarge
                )
                Text(
                    text = "Rang: ${userSeat.row} | Place: ${userSeat.seat}",
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.Medium
                )
            }
        }
        
        // Animation Status Display
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.secondaryContainer
            )
        ) {
            Column(
                modifier = Modifier.padding(20.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "🎨 Animation Couleur",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(12.dp))
                
                // Animation will appear in full screen when triggered
                Text(
                    text = animationStatus,
                    style = MaterialTheme.typography.bodyMedium,
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.onSecondaryContainer
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = "L'animation s'affichera en plein écran",
                    style = MaterialTheme.typography.bodySmall,
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.onSecondaryContainer.copy(alpha = 0.7f)
                )
                
                // Debug: Show animation frames info
                if (animationFrames != null) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "📦 Frames chargées: ${animationFrames?.size ?: 0}",
                        style = MaterialTheme.typography.bodySmall,
                        textAlign = TextAlign.Center,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
            }
        }
        
        // Statut de l'animation (utilise currentAnimation au lieu de scheduledAnimation)
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = if (currentAnimation?.isActive == true) 
                    MaterialTheme.colorScheme.secondaryContainer 
                else 
                    MaterialTheme.colorScheme.surfaceVariant
            )
        ) {
            Column(
                modifier = Modifier.padding(20.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                if (currentAnimation?.isActive == true) {
                    Text(
                        text = "🎆 Animation Programmée",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.primary
                    )
                    Spacer(modifier = Modifier.height(12.dp))
                    Text(
                        text = "Heure de début: ${formatDateTime(currentAnimation?.startTime ?: "")}",
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.Medium
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    // Indicateur de mise à jour en temps réel
                    if (isListening) {
                        Text(
                            text = "🔄 Mise à jour en temps réel",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.primary,
                            textAlign = TextAlign.Center
                        )
                        Text(
                            text = "Dernière mise à jour: ${formatUpdateTime(lastUpdateTime)}",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            textAlign = TextAlign.Center
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                    }
                    
                    Text(
                        text = "⏰ Restez connecté, l'animation va commencer!",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.secondary,
                        textAlign = TextAlign.Center
                    )
                } else {
                    Text(
                        text = "📱 En Attente",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(12.dp))
                    Text(
                        text = "Aucune animation programmée pour le moment.",
                        style = MaterialTheme.typography.bodyLarge,
                        textAlign = TextAlign.Center
                    )
                    
                    // Indicateur de mise à jour en temps réel
                    if (isListening) {
                        Text(
                            text = "🔄 Écoute des nouvelles animations...",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.primary,
                            textAlign = TextAlign.Center
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                    }
                    
                    Text(
                        text = "Nous vous notifierons dès qu'une animation sera disponible!",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.secondary,
                        textAlign = TextAlign.Center
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.weight(1f))
        
        // Bouton pour retourner à la sélection
        OutlinedButton(
            onClick = onBackToSeatSelection,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("← Retour à la sélection")
        }
            }
        }
        
        // Notification overlay pour les packages d'animation avec animation
        AnimatedVisibility(
            visible = showPackageNotification,
            enter = slideInVertically(
                initialOffsetY = { -it },
                animationSpec = tween(500)
            ) + fadeIn(animationSpec = tween(500)),
            exit = slideOutVertically(
                targetOffsetY = { -it },
                animationSpec = tween(300)
            ) + fadeOut(animationSpec = tween(300)),
            modifier = Modifier.align(Alignment.TopCenter)
        ) {
            PackageNotification(
                message = packageNotificationMessage
            )
        }
    }
}

// Fonction utilitaire pour formater les noms d'animation
private fun getAnimationDisplayName(animationType: String): String {
    return when (animationType) {
        "wave" -> "🌊 Vague"
        "rainbow" -> "🌈 Arc-en-ciel"
        "pulse" -> "💓 Pulsation"
        "fireworks" -> "🎆 Feux d'artifice"
        "blue_black_flash" -> "⚡ Flash Bleu/Noir"
        "checkboard_flash" -> "🏁 Flash Damier (Rouge/Bleu)"
        else -> animationType
    }
}

// Fonction utilitaire pour formater la date/heure
private fun formatDateTime(dateTimeString: String): String {
    return try {
        // Le format venant du HTML est "yyyy-MM-ddTHH:mm"
        val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
        val startTimeFormatted = if (dateTimeString.contains("T") && dateTimeString.length <= 16) {
            // Format from HTML datetime-local input: "2024-01-15T20:30"
            dateTimeString + ":00" // Add seconds if missing
        } else {
            dateTimeString
        }
        val date = inputFormat.parse(startTimeFormatted)
        val outputFormat = SimpleDateFormat("dd/MM/yyyy à HH:mm:ss", Locale.FRENCH)
        outputFormat.format(date)
    } catch (e: Exception) {
        try {
            // Essayons le format ISO 8601 complet
            val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
            val date = inputFormat.parse(dateTimeString.replace("Z", ""))
            val outputFormat = SimpleDateFormat("dd/MM/yyyy à HH:mm:ss", Locale.FRENCH)
            outputFormat.format(date)
        } catch (e2: Exception) {
            dateTimeString // Retourne la chaîne originale si le parsing échoue
        }
    }
}

// Fonction utilitaire pour formater l'heure de mise à jour
private fun formatUpdateTime(timestamp: Long): String {
    return try {
        val date = Date(timestamp)
        val formatter = SimpleDateFormat("HH:mm:ss", Locale.getDefault())
        formatter.format(date)
    } catch (e: Exception) {
        "N/A"
    }
}

// Composable pour afficher les notifications de package
@Composable
fun PackageNotification(
    message: String,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .padding(16.dp)
            .fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
    ) {
        Row(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Icône de notification
            Text(
                text = "📱",
                style = MaterialTheme.typography.headlineSmall,
                modifier = Modifier.padding(end = 12.dp)
            )
            
            // Message de notification
            Text(
                text = message,
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Medium,
                color = MaterialTheme.colorScheme.onPrimaryContainer,
                modifier = Modifier.weight(1f)
            )
            
            // Indicateur de fermeture automatique
            Text(
                text = "⏱️",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
            )
        }
    }
}

@Preview(showBackground = true)
@Composable
fun DefaultPreview() {
    MenuEventTheme {
        MainScreen(
            events = listOf(
                Event("Stade de foot", listOf("Nord", "Sud")),
                Event("Concert", listOf("Balcon", "Orchestre"))
            ),
            auth = FirebaseAuth.getInstance(),
            db = FirebaseFirestore.getInstance(),
            httpClient = OkHttpClient(),
            context = LocalContext.current
        )
    }
}

@Preview(showBackground = true)
@Composable
fun LoadingScreenPreview() {
    MenuEventTheme {
        LoadingScreen()
    }
}

@Preview(showBackground = true)
@Composable
fun WaitingRoomPreview() {
    MenuEventTheme {
        WaitingRoomScreen(
            userSeat = UserSeat(
                event = "Stade de foot",
                stand = "Tribune Nord",
                row = 12,
                seat = 45,
                userId = "user123"
            ),
            scheduledAnimation = ScheduledAnimation(
                animationType = "fireworks",
                eventType = "football_stadium",
                startTime = "2024-01-15T20:30",
                endTime = "2024-01-15T20:37",
                isActive = true
            ),
            onBackToSeatSelection = {}
        )
    }
}

@Preview(showBackground = true)
@Composable
fun WaitingRoomNoAnimationPreview() {
    MenuEventTheme {
        WaitingRoomScreen(
            userSeat = UserSeat(
                event = "Théâtre",
                stand = "Balcon",
                row = 5,
                seat = 12,
                userId = "user456"
            ),
            scheduledAnimation = null,
            onBackToSeatSelection = {}
        )
    }
}

@Preview(showBackground = true)
@Composable
fun PackageNotificationPreview() {
    MenuEventTheme {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp)
        ) {
            PackageNotification(
                message = "📦 Package d'animation reçu! 80 frames"
            )
            Spacer(modifier = Modifier.height(16.dp))
            PackageNotification(
                message = "🔄 Nouveau package d'animation! 60 frames"
            )
            Spacer(modifier = Modifier.height(16.dp))
            PackageNotification(
                message = "📦 Package d'animation supprimé"
            )
        }
    }
}

// Helper function to determine if a color is light
fun isLightColor(color: androidx.compose.ui.graphics.Color): Boolean {
    val luminance = 0.299 * color.red + 0.587 * color.green + 0.114 * color.blue
    return luminance > 0.5f
}
