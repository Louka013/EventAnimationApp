package com.example.eventanimationapp

import android.graphics.Color
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.widget.ImageView
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.firestore.ListenerRegistration
import kotlinx.coroutines.tasks.await
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Nouveau modèle de données pour les animations couleur
 */
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

data class ColorAnimationData(
    val animationId: String,
    val frameRate: Int,
    val frameCount: Int,
    val type: String,
    val startTime: String,
    val users: Map<String, ColorAnimationUser>
)

/**
 * Interface pour gérer les callbacks d'animation
 */
interface AnimationCallback {
    fun onAnimationLoaded(animationId: String, frameCount: Int)
    fun onAnimationStart(animationId: String)
    fun onAnimationFrame(frameIndex: Int, color: ColorFrame)
    fun onAnimationEnd(animationId: String)
    fun onAnimationError(error: String)
}

/**
 * Gestionnaire d'animation générique pour les animations couleur
 */
class AnimationPlayer {
    
    private val handler = Handler(Looper.getMainLooper())
    private var currentAnimationRunnable: Runnable? = null
    private var animationListener: ListenerRegistration? = null
    private var isPlaying = false
    
    companion object {
        private const val TAG = "AnimationPlayer"
        
        /**
         * Fonction générique pour charger et jouer une animation
         */
        fun loadAndPlayAnimation(
            animationId: String,
            row: Int,
            col: Int,
            callback: AnimationCallback
        ) {
            val player = AnimationPlayer()
            player.loadAnimation(animationId, row, col, callback)
        }
    }
    
    /**
     * Charge une animation depuis Firestore
     */
    private fun loadAnimation(
        animationId: String,
        row: Int,
        col: Int,
        callback: AnimationCallback
    ) {
        val db = FirebaseFirestore.getInstance()
        val userId = "user_${row}_${col}"
        
        Log.d(TAG, "Loading animation: $animationId for user: $userId")
        
        // Écouter les changements de l'animation principale
        animationListener = db.collection("animations")
            .document(animationId)
            .addSnapshotListener { documentSnapshot, error ->
                if (error != null) {
                    Log.e(TAG, "Error listening to animation: ${error.message}")
                    callback.onAnimationError("Erreur de connexion: ${error.message}")
                    return@addSnapshotListener
                }
                
                if (documentSnapshot != null && documentSnapshot.exists()) {
                    val animationData = documentSnapshot.data
                    if (animationData != null) {
                        val frameRate = (animationData["frameRate"] as? Number)?.toInt() ?: 2
                        val frameCount = (animationData["frameCount"] as? Number)?.toInt() ?: 20
                        val startTime = animationData["startTime"] as? String ?: ""
                        val animationType = animationData["type"] as? String ?: ""
                        
                        Log.d(TAG, "Animation data loaded: frameRate=$frameRate, frameCount=$frameCount, type=$animationType")
                        
                        if (animationType == "color_animation") {
                            // Charger les données utilisateur
                            loadUserColorData(animationId, userId, frameRate, frameCount, startTime, callback)
                        } else {
                            callback.onAnimationError("Type d'animation non supporté: $animationType")
                        }
                    }
                } else {
                    Log.d(TAG, "Animation document not found: $animationId")
                    callback.onAnimationError("Animation non trouvée: $animationId")
                }
            }
    }
    
    /**
     * Charge les données couleur spécifiques à l'utilisateur
     */
    private fun loadUserColorData(
        animationId: String,
        userId: String,
        frameRate: Int,
        frameCount: Int,
        startTime: String,
        callback: AnimationCallback
    ) {
        val db = FirebaseFirestore.getInstance()
        
        Log.d(TAG, "Loading user color data for: $userId")
        
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
                            
                            Log.d(TAG, "User colors loaded: ${colors.size} colors")
                            callback.onAnimationLoaded(animationId, colors.size)
                            
                            // Planifier l'animation
                            scheduleAnimation(animationId, colors, frameRate, startTime, callback)
                        } else {
                            callback.onAnimationError("Données de couleur manquantes pour l'utilisateur $userId")
                        }
                    }
                } else {
                    callback.onAnimationError("Utilisateur non trouvé: $userId")
                }
            }
            .addOnFailureListener { exception ->
                Log.e(TAG, "Error loading user data: ${exception.message}")
                callback.onAnimationError("Erreur de chargement: ${exception.message}")
            }
    }
    
    /**
     * Planifie l'animation selon le startTime
     */
    private fun scheduleAnimation(
        animationId: String,
        colors: List<ColorFrame>,
        frameRate: Int,
        startTime: String,
        callback: AnimationCallback
    ) {
        try {
            // Parser le startTime
            val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.getDefault())
            val startDate = dateFormat.parse(startTime.replace("Z", ""))
            val currentDate = Date()
            
            if (startDate == null) {
                Log.e(TAG, "Invalid start time format: $startTime")
                callback.onAnimationError("Format d'heure invalide: $startTime")
                return
            }
            
            val delayMs = startDate.time - currentDate.time
            
            if (delayMs > 0) {
                Log.d(TAG, "Scheduling animation to start in ${delayMs}ms")
                handler.postDelayed({
                    playAnimation(animationId, colors, frameRate, callback)
                }, delayMs)
            } else {
                Log.d(TAG, "Start time has passed, playing immediately")
                playAnimation(animationId, colors, frameRate, callback)
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Error scheduling animation: ${e.message}")
            callback.onAnimationError("Erreur de planification: ${e.message}")
        }
    }
    
    /**
     * Joue l'animation couleur
     */
    private fun playAnimation(
        animationId: String,
        colors: List<ColorFrame>,
        frameRate: Int,
        callback: AnimationCallback
    ) {
        if (isPlaying) {
            Log.d(TAG, "Animation already playing, stopping previous")
            stopAnimation()
        }
        
        isPlaying = true
        callback.onAnimationStart(animationId)
        
        val frameDurationMs = (1000.0 / frameRate).toLong()
        var currentFrame = 0
        
        Log.d(TAG, "Starting animation: $animationId with ${colors.size} colors at ${frameRate}fps")
        
        currentAnimationRunnable = object : Runnable {
            override fun run() {
                if (currentFrame < colors.size && isPlaying) {
                    val color = colors[currentFrame]
                    Log.d(TAG, "Playing frame $currentFrame: RGB(${color.r}, ${color.g}, ${color.b})")
                    
                    callback.onAnimationFrame(currentFrame, color)
                    currentFrame++
                    
                    handler.postDelayed(this, frameDurationMs)
                } else {
                    Log.d(TAG, "Animation finished: $animationId")
                    isPlaying = false
                    callback.onAnimationEnd(animationId)
                }
            }
        }
        
        currentAnimationRunnable?.run()
    }
    
    /**
     * Arrête l'animation en cours
     */
    fun stopAnimation() {
        isPlaying = false
        currentAnimationRunnable?.let { handler.removeCallbacks(it) }
        currentAnimationRunnable = null
        Log.d(TAG, "Animation stopped")
    }
    
    /**
     * Nettoie les ressources
     */
    fun cleanup() {
        stopAnimation()
        animationListener?.remove()
        animationListener = null
        Log.d(TAG, "Animation player cleaned up")
    }
}

/**
 * Composable pour afficher l'animation couleur
 */
@Composable
fun ColorAnimationView(
    animationId: String,
    row: Int,
    col: Int,
    modifier: androidx.compose.ui.Modifier = androidx.compose.ui.Modifier
) {
    var currentColor by remember { mutableStateOf(androidx.compose.ui.graphics.Color.Black) }
    var animationStatus by remember { mutableStateOf("Chargement...") }
    var isAnimationActive by remember { mutableStateOf(false) }
    
    val context = LocalContext.current
    
    LaunchedEffect(animationId, row, col) {
        val callback = object : AnimationCallback {
            override fun onAnimationLoaded(animationId: String, frameCount: Int) {
                animationStatus = "Animation chargée: $frameCount frames"
                Log.d("ColorAnimationView", "Animation loaded: $animationId")
            }
            
            override fun onAnimationStart(animationId: String) {
                animationStatus = "Animation en cours..."
                isAnimationActive = true
                Log.d("ColorAnimationView", "Animation started: $animationId")
            }
            
            override fun onAnimationFrame(frameIndex: Int, color: ColorFrame) {
                currentColor = androidx.compose.ui.graphics.Color(
                    red = color.r / 255f,
                    green = color.g / 255f,
                    blue = color.b / 255f,
                    alpha = 1f
                )
                Log.d("ColorAnimationView", "Frame $frameIndex: RGB(${color.r}, ${color.g}, ${color.b})")
            }
            
            override fun onAnimationEnd(animationId: String) {
                animationStatus = "Animation terminée"
                isAnimationActive = false
                Log.d("ColorAnimationView", "Animation ended: $animationId")
            }
            
            override fun onAnimationError(error: String) {
                animationStatus = "Erreur: $error"
                isAnimationActive = false
                Log.e("ColorAnimationView", "Animation error: $error")
            }
        }
        
        AnimationPlayer.loadAndPlayAnimation(animationId, row, col, callback)
    }
    
    // Interface utilisateur pour l'animation
    androidx.compose.foundation.layout.Column(
        modifier = modifier,
        horizontalAlignment = androidx.compose.ui.Alignment.CenterHorizontally
    ) {
        // Zone d'affichage de la couleur
        androidx.compose.foundation.Box(
            modifier = androidx.compose.ui.Modifier
                .fillMaxWidth()
                .height(200.dp)
                .background(currentColor)
        )
        
        androidx.compose.foundation.layout.Spacer(modifier = androidx.compose.ui.Modifier.height(16.dp))
        
        // Statut de l'animation
        androidx.compose.material3.Text(
            text = animationStatus,
            style = androidx.compose.material3.MaterialTheme.typography.bodyMedium
        )
        
        // Indicateur d'activité
        if (isAnimationActive) {
            androidx.compose.material3.LinearProgressIndicator(
                modifier = androidx.compose.ui.Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp)
            )
        }
    }
}

/**
 * Extension pour convertir ColorFrame en Color Android
 */
fun ColorFrame.toAndroidColor(): Int {
    return Color.rgb(this.r, this.g, this.b)
}

/**
 * Extension pour convertir ColorFrame en Color Compose
 */
fun ColorFrame.toComposeColor(): androidx.compose.ui.graphics.Color {
    return androidx.compose.ui.graphics.Color(
        red = this.r / 255f,
        green = this.g / 255f,
        blue = this.b / 255f,
        alpha = 1f
    )
}