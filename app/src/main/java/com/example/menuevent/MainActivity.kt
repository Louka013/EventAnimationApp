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
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.IOException
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit
import java.time.Instant
import java.time.ZoneId

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

data class AnimationUser(
    val frames: List<String>
)

data class AnimationData(
    val animationId: String,
    val frameRate: Int,
    val frameCount: Int,
    val users: Map<String, AnimationUser>
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
                val startDateTime = if (startTime.contains("T") && startTime.length <= 16) {
                    // Format from HTML datetime-local input: "2024-01-15T20:30"
                    LocalDateTime.parse(startTime + ":00") // Add seconds if missing
                } else {
                    // Try to parse as is
                    LocalDateTime.parse(startTime)
                }
                
                val durationSeconds = frameCount.toDouble() / frameRate.toDouble()
                Log.d("Animation", "Animation duration: ${durationSeconds} seconds")
                
                val endDateTime = startDateTime.plusSeconds(durationSeconds.toLong())
                val result = endDateTime.toString()
                
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
                val endDateTime = LocalDateTime.parse(endTime)
                val currentDateTime = LocalDateTime.now()
                currentDateTime.isAfter(endDateTime)
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
        
        val users = mutableMapOf<String, AnimationUser>()
        usersJson.keys().forEach { key ->
            val userJson = usersJson.getJSONObject(key)
            val framesArray = userJson.getJSONArray("frames")
            val frames = mutableListOf<String>()
            for (i in 0 until framesArray.length()) {
                frames.add(framesArray.getString(i))
            }
            users[key] = AnimationUser(frames)
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
                                val users = mutableMapOf<String, AnimationUser>()
                                
                                usersMap?.forEach { (userId, userData) ->
                                    val userDataMap = userData as? Map<String, Any>
                                    val frames = userDataMap?.get("frames") as? List<String> ?: listOf()
                                    users[userId] = AnimationUser(frames)
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
            
            val users = mutableMapOf<String, AnimationUser>()
            usersJson.keys().forEach { key ->
                val userJson = usersJson.getJSONObject(key)
                val framesArray = userJson.getJSONArray("frames")
                val frames = mutableListOf<String>()
                for (i in 0 until framesArray.length()) {
                    frames.add(framesArray.getString(i))
                }
                users[key] = AnimationUser(frames)
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

    // Détermine si le bouton "Valider" doit être activé
    val isValidationEnabled = selectedEvent != null &&
            selectedStand != null &&
            selectedRow != null &&
            selectedSeat != null

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
            }
        )
    } else {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text("Sélectionnez votre place", style = MaterialTheme.typography.headlineSmall)
            
            // Statut de l'animation
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = if (activeAnimationConfig != null) 
                        MaterialTheme.colorScheme.primaryContainer 
                    else 
                        MaterialTheme.colorScheme.surfaceVariant
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "🎭 Statut Animation",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = animationStatus,
                        style = MaterialTheme.typography.bodyMedium,
                        textAlign = TextAlign.Center
                    )
                }
            }

            // Sélecteur d'événement
            EventDropdown(
                events = events,
                selectedEvent = selectedEvent,
                onEventSelected = { event ->
                    selectedEvent = event
                    selectedStand = null // Réinitialiser la tribune lors du changement d'événement
                    // selectedRow = null // Optionnel: réinitialiser aussi rang et place
                    // selectedSeat = null
                }
            )

            // Sélecteur de tribune (n'apparaît que si un événement est sélectionné)
            selectedEvent?.let { event ->
                StandDropdown(
                    stands = event.stands,
                    selectedStand = selectedStand,
                    onStandSelected = { stand ->
                        selectedStand = stand
                    }
                )
            }

            // Sélecteur de rang
            NumberDropdown(
                label = "Rang",
                range = 1..30,
                selectedValue = selectedRow,
                onValueSelected = { row ->
                    selectedRow = row
                }
            )

            // Sélecteur de numéro de place
            NumberDropdown(
                label = "Numéro de place",
                range = 1..40,
                selectedValue = selectedSeat,
                onValueSelected = { seat ->
                    selectedSeat = seat
                }
            )

            Spacer(modifier = Modifier.weight(1f)) // Pour pousser le bouton vers le bas

            Button(
                onClick = {
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
                },
                enabled = isValidationEnabled,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Valider")
            }
            
            // Bouton pour déclencher manuellement l'animation
            if (activeAnimationConfig != null) {
                Button(
                    onClick = {
                        coroutineScope.launch {
                            try {
                                val authResult = auth.signInAnonymously().await()
                                val userId = authResult.user?.uid ?: ""
                                
                                val animationTriggered = MainActivity.triggerAnimation(
                                    httpClient,
                                    activeAnimationConfig!!.animationType,
                                    "user_${selectedRow ?: 1}_${selectedSeat ?: 1}"
                                )
                                
                                if (animationTriggered) {
                                    Toast.makeText(context, "Animation déclenchée!", Toast.LENGTH_SHORT).show()
                                } else {
                                    Toast.makeText(context, "Erreur lors du déclenchement", Toast.LENGTH_SHORT).show()
                                }
                            } catch (e: Exception) {
                                Log.e("Animation", "Erreur: ${e.message}")
                                Toast.makeText(context, "Erreur: ${e.message}", Toast.LENGTH_LONG).show()
                            }
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.secondary
                    )
                ) {
                    Text("🎭 Déclencher Animation")
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
fun WaitingRoomScreen(
    userSeat: UserSeat,
    scheduledAnimation: ScheduledAnimation?,
    onBackToSeatSelection: () -> Unit
) {
    // État pour l'animation en temps réel
    var currentAnimation by remember { mutableStateOf(scheduledAnimation) }
    var isListening by remember { mutableStateOf(false) }
    var lastUpdateTime by remember { mutableStateOf(System.currentTimeMillis()) }
    
    // Déterminer le type d'événement pour le listener
    val eventTypeForAnimation = remember {
        when (userSeat.event) {
            "Stade de foot" -> "football_stadium"
            "Salle de concert" -> "concert_hall"
            "Théâtre" -> "theater"
            else -> "general"
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
                    }
                } else {
                    Log.d("Animation", "No active animations found")
                    if (currentAnimation != null) {
                        currentAnimation = null
                        lastUpdateTime = System.currentTimeMillis()
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
                        text = "Type: ${getAnimationDisplayName(currentAnimation?.animationType ?: "")}",
                        style = MaterialTheme.typography.bodyLarge
                    )
                    Text(
                        text = "Heure de début: ${formatDateTime(currentAnimation?.startTime ?: "")}",
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = "Heure de fin: ${formatDateTime(currentAnimation?.endTime ?: "")}",
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

// Fonction utilitaire pour formater les noms d'animation
private fun getAnimationDisplayName(animationType: String): String {
    return when (animationType) {
        "wave" -> "🌊 Vague"
        "rainbow" -> "🌈 Arc-en-ciel"
        "pulse" -> "💓 Pulsation"
        "fireworks" -> "🎆 Feux d'artifice"
        else -> animationType
    }
}

// Fonction utilitaire pour formater la date/heure
private fun formatDateTime(dateTimeString: String): String {
    return try {
        // Le format venant du HTML est "yyyy-MM-ddTHH:mm"
        val inputDate = if (dateTimeString.contains("T") && dateTimeString.length <= 16) {
            // Format from HTML datetime-local input: "2024-01-15T20:30"
            LocalDateTime.parse(dateTimeString + ":00") // Add seconds if missing
        } else {
            LocalDateTime.parse(dateTimeString)
        }
        val formatter = DateTimeFormatter.ofPattern("dd/MM/yyyy à HH:mm:ss")
        inputDate.format(formatter)
    } catch (e: Exception) {
        try {
            // Essayons le format ISO 8601 complet
            val inputDate = LocalDateTime.parse(dateTimeString.replace("Z", ""))
            val formatter = DateTimeFormatter.ofPattern("dd/MM/yyyy à HH:mm:ss")
            inputDate.format(formatter)
        } catch (e2: Exception) {
            dateTimeString // Retourne la chaîne originale si le parsing échoue
        }
    }
}

// Fonction utilitaire pour formater l'heure de mise à jour
private fun formatUpdateTime(timestamp: Long): String {
    return try {
        val updateTime = LocalDateTime.ofInstant(
            java.time.Instant.ofEpochMilli(timestamp), 
            java.time.ZoneId.systemDefault()
        )
        val formatter = DateTimeFormatter.ofPattern("HH:mm:ss")
        updateTime.format(formatter)
    } catch (e: Exception) {
        "N/A"
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
