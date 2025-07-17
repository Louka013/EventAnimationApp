package com.example.menuevent

import android.util.Log
import com.google.firebase.database.DataSnapshot
import com.google.firebase.database.DatabaseError
import com.google.firebase.database.FirebaseDatabase
import com.google.firebase.database.ValueEventListener
import com.google.firebase.firestore.FieldValue
import com.google.firebase.firestore.FirebaseFirestore
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withTimeout
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

class TimeSynchronizationManager {
    companion object {
        private const val TAG = "TimeSyncManager"
        private const val SYNC_TIMEOUT_MS = 5000L
        
        @Volatile
        private var instance: TimeSynchronizationManager? = null
        
        fun getInstance(): TimeSynchronizationManager {
            return instance ?: synchronized(this) {
                instance ?: TimeSynchronizationManager().also { instance = it }
            }
        }
    }
    
    private val database = FirebaseDatabase.getInstance()
    private val firestore = FirebaseFirestore.getInstance()
    
    // Cache for server time offset
    @Volatile
    private var serverTimeOffset: Long = 0L
    private var offsetListener: ValueEventListener? = null
    
    /**
     * Initialize time synchronization
     */
    fun initialize() {
        startServerTimeSync()
    }
    
    /**
     * Start listening for server time offset updates
     */
    private fun startServerTimeSync() {
        val offsetRef = database.getReference(".info/serverTimeOffset")
        offsetListener = object : ValueEventListener {
            override fun onDataChange(snapshot: DataSnapshot) {
                val offset = snapshot.getValue(Long::class.java) ?: 0L
                serverTimeOffset = offset
                Log.d(TAG, "Server time offset updated: ${offset}ms")
            }
            
            override fun onCancelled(error: DatabaseError) {
                Log.e(TAG, "Server time offset listener cancelled: ${error.message}")
            }
        }
        offsetRef.addValueEventListener(offsetListener!!)
    }
    
    /**
     * Stop listening for server time offset updates
     */
    fun cleanup() {
        offsetListener?.let { listener ->
            database.getReference(".info/serverTimeOffset").removeEventListener(listener)
        }
        offsetListener = null
    }
    
    /**
     * Get current server time estimate
     */
    fun getServerTime(): Long {
        return System.currentTimeMillis() + serverTimeOffset
    }
    
    /**
     * Calculate delay until target server time
     */
    fun calculateDelayUntilServerTime(targetServerTime: Long): Long {
        val currentServerTime = getServerTime()
        return targetServerTime - currentServerTime
    }
    
    /**
     * Get server timestamp using Firestore (more accurate for critical operations)
     */
    suspend fun getFirestoreServerTimestamp(): Long = withTimeout(SYNC_TIMEOUT_MS) {
        suspendCancellableCoroutine { continuation ->
            val tempDoc = firestore.collection("temp_time_sync").document()
            tempDoc.set(mapOf("timestamp" to FieldValue.serverTimestamp()))
                .addOnSuccessListener {
                    tempDoc.get().addOnSuccessListener { document ->
                        val timestamp = document.getTimestamp("timestamp")
                        if (timestamp != null) {
                            continuation.resume(timestamp.toDate().time)
                            // Clean up temp document
                            tempDoc.delete()
                        } else {
                            continuation.resumeWithException(Exception("Failed to get server timestamp"))
                        }
                    }.addOnFailureListener { exception ->
                        continuation.resumeWithException(exception)
                    }
                }.addOnFailureListener { exception ->
                    continuation.resumeWithException(exception)
                }
        }
    }
    
    /**
     * Synchronize local time with server and return offset
     */
    suspend fun synchronizeTime(): TimeSync {
        return try {
            val localTimeStart = System.currentTimeMillis()
            val serverTime = getFirestoreServerTimestamp()
            val localTimeEnd = System.currentTimeMillis()
            
            // Calculate network delay
            val networkDelay = (localTimeEnd - localTimeStart) / 2
            val adjustedServerTime = serverTime + networkDelay
            
            // Calculate offset
            val offset = adjustedServerTime - localTimeEnd
            
            Log.d(TAG, "Time synchronization complete: offset=${offset}ms, networkDelay=${networkDelay}ms")
            
            TimeSync(
                offset = offset,
                networkDelay = networkDelay,
                accuracy = if (networkDelay < 100) TimeSyncAccuracy.HIGH else TimeSyncAccuracy.MEDIUM,
                timestamp = System.currentTimeMillis()
            )
        } catch (e: Exception) {
            Log.e(TAG, "Time synchronization failed: ${e.message}")
            TimeSync(
                offset = serverTimeOffset,
                networkDelay = 0,
                accuracy = TimeSyncAccuracy.LOW,
                timestamp = System.currentTimeMillis()
            )
        }
    }
    
    /**
     * Get current sync status
     */
    fun getSyncStatus(): String {
        return "Server time offset: ${serverTimeOffset}ms"
    }
}

data class TimeSync(
    val offset: Long,
    val networkDelay: Long,
    val accuracy: TimeSyncAccuracy,
    val timestamp: Long
)

enum class TimeSyncAccuracy {
    HIGH,    // Network delay < 100ms
    MEDIUM,  // Network delay 100-500ms
    LOW      // Network delay > 500ms or fallback to Realtime DB offset
}