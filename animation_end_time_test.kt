// Test script to demonstrate animation end time calculation
// This shows how the new logic works

import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

fun calculateEndTime(startTime: String, frameCount: Int, frameRate: Int): String {
    return try {
        val startDateTime = LocalDateTime.parse(startTime)
        val durationSeconds = frameCount.toDouble() / frameRate.toDouble()
        val endDateTime = startDateTime.plusSeconds(durationSeconds.toLong())
        endDateTime.toString()
    } catch (e: Exception) {
        println("Error calculating end time: ${e.message}")
        startTime // Fallback to start time if calculation fails
    }
}

fun isAnimationExpired(endTime: String): Boolean {
    return try {
        val endDateTime = LocalDateTime.parse(endTime)
        val currentDateTime = LocalDateTime.now()
        currentDateTime.isAfter(endDateTime)
    } catch (e: Exception) {
        println("Error checking expiration: ${e.message}")
        false // If we can't parse, assume not expired
    }
}

fun main() {
    println("=== Animation End Time Calculation Test ===")
    
    // Test cases with different animation types
    val testCases = listOf(
        Triple("Wave Animation", "2024-01-15T20:30:00", Triple(80, 15, "wave")),
        Triple("Rainbow Animation", "2024-01-15T20:30:00", Triple(60, 12, "rainbow")),
        Triple("Pulse Animation", "2024-01-15T20:30:00", Triple(40, 8, "pulse")),
        Triple("Fireworks Animation", "2024-01-15T20:30:00", Triple(120, 18, "fireworks"))
    )
    
    val formatter = DateTimeFormatter.ofPattern("dd/MM/yyyy à HH:mm:ss")
    
    testCases.forEach { (name, startTime, animationData) ->
        val (frameCount, frameRate, type) = animationData
        val endTime = calculateEndTime(startTime, frameCount, frameRate)
        val isExpired = isAnimationExpired(endTime)
        
        val startFormatted = LocalDateTime.parse(startTime).format(formatter)
        val endFormatted = LocalDateTime.parse(endTime).format(formatter)
        val duration = frameCount.toDouble() / frameRate.toDouble()
        
        println("\n--- $name ---")
        println("Type: $type")
        println("Frames: $frameCount")
        println("Frame Rate: $frameRate fps")
        println("Duration: ${duration.toInt()} seconds")
        println("Start: $startFormatted")
        println("End: $endFormatted")
        println("Expired: ${if (isExpired) "✅ Yes" else "❌ No"}")
    }
    
    println("\n=== Testing Expiration Logic ===")
    
    // Test with current time
    val now = LocalDateTime.now()
    val pastTime = now.minusMinutes(10).toString()
    val futureTime = now.plusMinutes(10).toString()
    
    println("Current time: ${now.format(formatter)}")
    println("Past animation end time: ${LocalDateTime.parse(pastTime).format(formatter)} -> Expired: ${isAnimationExpired(pastTime)}")
    println("Future animation end time: ${LocalDateTime.parse(futureTime).format(formatter)} -> Expired: ${isAnimationExpired(futureTime)}")
}