import {
  S3RequestPresigner,
  getSignedUrl,
} from "@aws-sdk/s3-request-presigner"; 
import {
  S3Client,
  PutObjectCommand,
} from "@aws-sdk/client-s3";

export default {
  async fetch(request, env) {
    // We only handle POST /get-presigned-url
    const url = new URL(request.url);
    if (request.method === "POST" && url.pathname === "/get-presigned-url") {
      // 1. Parse JSON body, expecting: { incidentId: "incident_YYYYMMDD-HHMMSS" }
      const data = await request.json().catch(() => null);
      if (!data || !data.incidentId) {
        return new Response("Missing incidentId in JSON body", { status: 400 });
      }

      // 2. Construct an S3Client that points to your R2 bucket
      //    The "endpoint" is critical. It's your R2 public hostname, e.g. https://<ACCOUNT_ID>.r2.cloudflarestorage.com
      //    The region can be anything, but "auto" is often used for R2.
      //    Provide accessKeyId/secretAccessKey from your environment (API tokens for R2).
      const s3Client = new S3Client({
        endpoint: env.MY_R2,
        region: "auto",
        endpoint: process.env.R2_ENDPOINT,
          credentials: {
            accessKeyId: env.R2_ACCESS_KEY_ID,
            secretAccessKey: env.R2_SECRET_ACCESS_KEY,
          },
        forcePathStyle: true, // R2 uses path-style
      });

      // 3. Create a PutObjectCommand for the key incidents/<incidentId>.mp4
      const key = `incidents/${data.incidentId}.mp4`;
      const command = new PutObjectCommand({
        Bucket: "watchdog-incident-reports", // your R2 bucket name
        Key: key,
      });

      // 4. Generate a presigned URL that expires in e.g. 10 minutes (600 seconds)
      //    So the client can do a direct PUT to that URL.
      const signedUrl = await getSignedUrl(s3Client, command, { expiresIn: 600 });

      // 5. Return JSON with the presigned URL
      return new Response(
        JSON.stringify({ 
          uploadUrl: signedUrl,
          key: key
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    return new Response("Not Found", { status: 404 });
  },
};