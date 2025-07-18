const {onRequest} = require("firebase-functions/v2/https");
const {logger} = require("firebase-functions");
const admin = require("firebase-admin");

admin.initializeApp();

// Get animation data by type
exports.getAnimation = onRequest({cors: true}, async (req, res) => {
  try {
    const animationType = req.query.type;
    
    if (!animationType) {
      return res.status(400).json({error: "Animation type is required"});
    }
    
    const db = admin.firestore();
    const animationDoc = await db.collection('animations').doc(animationType).get();
    
    if (!animationDoc.exists) {
      return res.status(404).json({error: "Animation not found"});
    }
    
    const animationData = animationDoc.data();
    
    // Add CORS headers
    res.set('Access-Control-Allow-Origin', '*');
    res.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.set('Access-Control-Allow-Headers', 'Content-Type');
    
    res.json(animationData);
  } catch (error) {
    logger.error("Error fetching animation:", error);
    res.status(500).json({error: "Internal server error"});
  }
});

// Get all available animations
exports.getAllAnimations = onRequest({cors: true}, async (req, res) => {
  try {
    const db = admin.firestore();
    const animationsSnapshot = await db.collection('animations').get();
    
    const animations = {};
    animationsSnapshot.forEach(doc => {
      animations[doc.id] = doc.data();
    });
    
    // Add CORS headers
    res.set('Access-Control-Allow-Origin', '*');
    res.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.set('Access-Control-Allow-Headers', 'Content-Type');
    
    res.json(animations);
  } catch (error) {
    logger.error("Error fetching animations:", error);
    res.status(500).json({error: "Internal server error"});
  }
});

// Get active animation configs
exports.getActiveConfig = onRequest({cors: true}, async (req, res) => {
  try {
    const db = admin.firestore();
    
    // Add detailed logging
    logger.info("Fetching active animation configs...");
    
    let configsSnapshot;
    try {
      // Try with ordering first
      configsSnapshot = await db.collection('animation_configs')
        .where('status', '==', 'active')
        .orderBy('createdAt', 'desc')
        .limit(1)
        .get();
    } catch (orderError) {
      logger.warn("Could not order by createdAt, trying without ordering:", orderError);
      // If ordering fails (likely due to missing index), try without ordering
      configsSnapshot = await db.collection('animation_configs')
        .where('status', '==', 'active')
        .limit(1)
        .get();
    }
    
    logger.info(`Found ${configsSnapshot.docs.length} active configs`);
    
    if (configsSnapshot.empty) {
      // Let's also check if there are any configs at all
      const allConfigsSnapshot = await db.collection('animation_configs').get();
      logger.info(`Total configs in database: ${allConfigsSnapshot.docs.length}`);
      
      if (!allConfigsSnapshot.empty) {
        allConfigsSnapshot.docs.forEach(doc => {
          const data = doc.data();
          logger.info(`Config found: status=${data.status}, eventType=${data.eventType}, animationType=${data.animationType}`);
        });
      }
      
      return res.status(404).json({error: "No active configuration found"});
    }
    
    const config = configsSnapshot.docs[0].data();
    logger.info(`Returning config: ${JSON.stringify(config)}`);
    
    // Add CORS headers
    res.set('Access-Control-Allow-Origin', '*');
    res.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.set('Access-Control-Allow-Headers', 'Content-Type');
    
    res.json(config);
  } catch (error) {
    logger.error("Error fetching active config:", error);
    res.status(500).json({error: "Internal server error"});
  }
});

// Trigger animation for Android app
exports.triggerAnimation = onRequest({cors: true}, async (req, res) => {
  try {
    const {animationType, userId, startTime} = req.body;
    
    if (!animationType || !userId) {
      return res.status(400).json({error: "Animation type and user ID are required"});
    }
    
    const db = admin.firestore();
    
    // Get animation data
    const animationDoc = await db.collection('animations').doc(animationType).get();
    
    if (!animationDoc.exists) {
      return res.status(404).json({error: "Animation not found"});
    }
    
    const animationData = animationDoc.data();
    
    // Create trigger record
    const triggerData = {
      animationType,
      userId,
      animationData,
      startTime: startTime || admin.firestore.FieldValue.serverTimestamp(),
      status: 'triggered',
      createdAt: admin.firestore.FieldValue.serverTimestamp()
    };
    
    const triggerRef = await db.collection('animation_triggers').add(triggerData);
    
    // Add CORS headers
    res.set('Access-Control-Allow-Origin', '*');
    res.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.set('Access-Control-Allow-Headers', 'Content-Type');
    
    res.json({
      success: true,
      triggerId: triggerRef.id,
      animationData
    });
  } catch (error) {
    logger.error("Error triggering animation:", error);
    res.status(500).json({error: "Internal server error"});
  }
});