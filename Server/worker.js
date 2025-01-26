import { Ai } from '@cloudflare/ai';

export default {
  async fetch(request, env) {
    try {
      if (request.method === 'OPTIONS') {
        return corsResponse(null);
      }

      if (request.method !== 'POST') {
        return corsResponse({ error: 'Method not allowed' }, 405);
      }

      const formData = await request.formData();
      const imageBlob = formData.get('image');
      const motionDataStr = formData.get('motion_data');

      if (!imageBlob || !motionDataStr) {
        return corsResponse({ 
          error: 'Missing required data',
          suspicious: false,
          requires_attention: false
        }, 400);
      }

      const motionData = JSON.parse(motionDataStr);
      const ai = new Ai(env.AI);
      const imageBytes = await imageBlob.arrayBuffer();

      const [objectDetection, safetyCheck] = await Promise.all([
        ai.run('@cf/microsoft/resnet-50', {
          image: [...new Uint8Array(imageBytes)],
        }),
        ai.run('@cf/microsoft/dit-base', {
          image: [...new Uint8Array(imageBytes)],
        }),
      ]);

      const threatScore = calculateThreatScore(objectDetection, safetyCheck, motionData);

      return corsResponse({
        suspicious: threatScore > 0.5,
        threat_score: threatScore,
        detections: objectDetection,
        requires_attention: false
      });

    } catch (error) {
      console.error('Error:', error);
      return corsResponse({
        error: error.message,
        suspicious: false,
        requires_attention: false
      }, 500);
    }
  },
};

function calculateThreatScore(objectDetection, safetyCheck, motionData) {
  let score = 0;
  
  // Base motion score
  const motionScore = Math.min(motionData.area / 15000, 0.4);
  score += motionScore;

  // Check for suspicious objects with confidence weighting
  const suspiciousObjects = {
    'knife': 0.3,
    'gun': 0.4,
    'weapon': 0.4,
    'mask': 0.2,
    'person': 0.1
  };

  objectDetection.objects?.forEach(obj => {
    const label = obj.label?.toLowerCase();
    if (suspiciousObjects[label]) {
      score += suspiciousObjects[label] * obj.confidence;
    }
  });

  // Factor in safety check scores
  if (safetyCheck.violence > 0.6) score += 0.3;
  if (safetyCheck.weapons > 0.5) score += 0.2;

  // Cap final score at 1.0
  return Math.min(score, 1.0);
}

function corsResponse(data, status = 200) {
  return new Response(
    JSON.stringify(data),
    {
      status,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    }
  );
}