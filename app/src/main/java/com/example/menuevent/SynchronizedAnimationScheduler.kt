package com.example.menuevent

import android.os.Handler
import android.os.Looper
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

class SynchronizedAnimationScheduler {
    companion object {
        private const val TAG = "SyncAnimationScheduler"
        private const val PRECISION_SYNC_THRESHOLD = 1000L // 1 second
        private const val FALLBACK_SYNC_THRESHOLD = 5000L // 5 seconds
    }
    
    private val timeSyncManager = TimeSynchronizationManager.getInstance()
    private val scope = CoroutineScope(Dispatchers.Main)
    private val handler = Handler(Looper.getMainLooper())
    
    /**
     * Schedule animation with server time synchronization
     */
    fun scheduleAnimation(
        animationId: String,
        startTimeString: String,
        colors: List<ColorFrame>,
        frameRate: Int,
        onAnimationStart: () -> Unit,
        onAnimationFrame: (ColorFrame) -> Unit,
        onAnimationEnd: () -> Unit,
        onAnimationError: (String) -> Unit
    ) {
        scope.launch {
            try {
                // Parse start time
                val startTime = parseAnimationTime(startTimeString)
                if (startTime == null) {
                    onAnimationError("Invalid start time format: $startTimeString")
                    return@launch
                }
                
                // Get time synchronization
                val timeSync = timeSyncManager.synchronizeTime()
                val serverTime = System.currentTimeMillis() + timeSync.offset
                
                // Calculate delay with server time
                val delayMs = startTime.time - serverTime
                
                Log.d(TAG, "Animation scheduling:")
                Log.d(TAG, "  - Animation ID: $animationId")
                Log.d(TAG, "  - Start time: $startTimeString")
                Log.d(TAG, "  - Server time: ${Date(serverTime)}")
                Log.d(TAG, "  - Delay: ${delayMs}ms")
                Log.d(TAG, "  - Sync accuracy: ${timeSync.accuracy}")
                Log.d(TAG, "  - Network delay: ${timeSync.networkDelay}ms")
                
                when {
                    delayMs <= 0 -> {
                        // Allow animation to start if it's only slightly late (normal network/sync delays)
                        // But prevent it if it's too old (user just entered waiting room)
                        if (delayMs > -10000) { // Allow up to 10 seconds of lateness
                            Log.w(TAG, "Animation start time has passed recently (${delayMs}ms), starting immediately")
                            // Start animation immediately using precise timing
                            scope.launch {
                                onAnimationStart()
                                val frameDelayMs = (1000.0 / frameRate).toLong()
                                for ((index, color) in colors.withIndex()) {
                                    val frameStartTime = System.currentTimeMillis()
                                    onAnimationFrame(color)
                                    if (index < colors.size - 1) {
                                        val frameEndTime = System.currentTimeMillis()
                                        val processingTime = frameEndTime - frameStartTime
                                        val remainingDelay = maxOf(0, frameDelayMs - processingTime)
                                        if (remainingDelay > 0) {
                                            delay(remainingDelay)
                                        }
                                    }
                                }
                                onAnimationEnd()
                            }
                        } else {
                            Log.w(TAG, "Animation start time has passed too long ago (${delayMs}ms), waiting for next scheduled start time")
                            onAnimationError("Animation start time has passed, waiting for next scheduled start time")
                        }
                    }
                    delayMs > FALLBACK_SYNC_THRESHOLD && timeSync.accuracy == TimeSyncAccuracy.LOW -> {
                        Log.w(TAG, "Using fallback timing due to poor synchronization")
                        scheduleWithFallbackTiming(delayMs, colors, frameRate, onAnimationStart, onAnimationFrame, onAnimationEnd)
                    }
                    else -> {
                        scheduleWithPreciseTiming(delayMs, colors, frameRate, onAnimationStart, onAnimationFrame, onAnimationEnd)
                    }
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Error scheduling animation: ${e.message}")
                onAnimationError("Error scheduling animation: ${e.message}")
            }
        }
    }
    
    /**
     * Schedule with precise timing (high accuracy sync)
     */
    private suspend fun scheduleWithPreciseTiming(
        delayMs: Long,
        colors: List<ColorFrame>,
        frameRate: Int,
        onAnimationStart: () -> Unit,
        onAnimationFrame: (ColorFrame) -> Unit,
        onAnimationEnd: () -> Unit
    ) {
        Log.d(TAG, "Using precise timing synchronization")
        
        // Wait for start time
        delay(delayMs)
        
        // Start animation
        onAnimationStart()
        
        // Play animation frames
        val frameDelayMs = (1000.0 / frameRate).toLong()
        
        for ((index, color) in colors.withIndex()) {
            val frameStartTime = System.currentTimeMillis()
            onAnimationFrame(color)
            
            // Precise frame timing
            if (index < colors.size - 1) {
                val frameEndTime = System.currentTimeMillis()
                val processingTime = frameEndTime - frameStartTime
                val remainingDelay = maxOf(0, frameDelayMs - processingTime)
                
                if (remainingDelay > 0) {
                    delay(remainingDelay)
                }
            }
        }
        
        onAnimationEnd()
    }
    
    /**
     * Schedule with fallback timing (lower accuracy)
     */
    private suspend fun scheduleWithFallbackTiming(
        delayMs: Long,
        colors: List<ColorFrame>,
        frameRate: Int,
        onAnimationStart: () -> Unit,
        onAnimationFrame: (ColorFrame) -> Unit,
        onAnimationEnd: () -> Unit
    ) {
        Log.d(TAG, "Using fallback timing synchronization")
        
        // Use simpler delay mechanism
        delay(delayMs)
        onAnimationStart()
        
        val frameDelayMs = (1000.0 / frameRate).toLong()
        
        for ((index, color) in colors.withIndex()) {
            onAnimationFrame(color)
            if (index < colors.size - 1) {
                delay(frameDelayMs)
            }
        }
        
        onAnimationEnd()
    }
    
    /**
     * Legacy method for backward compatibility with existing Handler-based system
     */
    fun scheduleAnimationLegacy(
        animationId: String,
        startTimeString: String,
        colors: List<ColorFrame>,
        frameRate: Int,
        onAnimationStart: () -> Unit,
        onAnimationFrame: (ColorFrame) -> Unit,
        onAnimationEnd: () -> Unit,
        onAnimationError: (String) -> Unit
    ) {
        try {
            // Parse start time
            val startTime = parseAnimationTime(startTimeString)
            if (startTime == null) {
                onAnimationError("Invalid start time format: $startTimeString")
                return
            }
            
            // Use server time for synchronization
            val serverTime = timeSyncManager.getServerTime()
            val delayMs = startTime.time - serverTime
            
            Log.d(TAG, "Legacy animation scheduling:")
            Log.d(TAG, "  - Animation ID: $animationId")
            Log.d(TAG, "  - Start time: $startTimeString")
            Log.d(TAG, "  - Server time: ${Date(serverTime)}")
            Log.d(TAG, "  - Delay: ${delayMs}ms")
            Log.d(TAG, "  - Sync status: ${timeSyncManager.getSyncStatus()}")
            
            if (delayMs <= 0) {
                // Allow animation to start if it's only slightly late (normal network/sync delays)
                // But prevent it if it's too old (user just entered waiting room)
                if (delayMs > -10000) { // Allow up to 10 seconds of lateness
                    Log.w(TAG, "Animation start time has passed recently (${delayMs}ms), starting immediately")
                    playAnimationFrames(colors, frameRate, onAnimationStart, onAnimationFrame, onAnimationEnd)
                } else {
                    Log.w(TAG, "Animation start time has passed too long ago (${delayMs}ms), waiting for next scheduled start time")
                    onAnimationError("Animation start time has passed, waiting for next scheduled start time")
                }
            } else {
                // Schedule using Handler
                handler.postDelayed({
                    playAnimationFrames(colors, frameRate, onAnimationStart, onAnimationFrame, onAnimationEnd)
                }, delayMs)
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Error scheduling legacy animation: ${e.message}")
            onAnimationError("Error scheduling animation: ${e.message}")
        }
    }
    
    /**
     * Play animation frames using Handler
     */
    private fun playAnimationFrames(
        colors: List<ColorFrame>,
        frameRate: Int,
        onAnimationStart: () -> Unit,
        onAnimationFrame: (ColorFrame) -> Unit,
        onAnimationEnd: () -> Unit
    ) {
        onAnimationStart()
        
        val frameDelayMs = (1000.0 / frameRate).toLong()
        var currentIndex = 0
        
        val frameRunnable = object : Runnable {
            override fun run() {
                if (currentIndex < colors.size) {
                    onAnimationFrame(colors[currentIndex])
                    currentIndex++
                    
                    if (currentIndex < colors.size) {
                        handler.postDelayed(this, frameDelayMs)
                    } else {
                        onAnimationEnd()
                    }
                }
            }
        }
        
        frameRunnable.run()
    }
    
    /**
     * Parse animation time string to Date object
     */
    private fun parseAnimationTime(timeString: String): Date? {
        return try {
            when {
                timeString.endsWith("Z") -> {
                    try {
                        SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.getDefault()).parse(timeString)
                    } catch (e: Exception) {
                        SimpleDateFormat("yyyy-MM-dd'T'HH:mm'Z'", Locale.getDefault()).parse(timeString)
                    }
                }
                timeString.contains("T") -> {
                    try {
                        SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault()).parse(timeString)
                    } catch (e: Exception) {
                        SimpleDateFormat("yyyy-MM-dd'T'HH:mm", Locale.getDefault()).parse(timeString)
                    }
                }
                else -> {
                    SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).parse(timeString)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to parse time: $timeString", e)
            null
        }
    }
    
    /**
     * Get synchronization status
     */
    fun getSyncStatus(): String {
        return timeSyncManager.getSyncStatus()
    }
}