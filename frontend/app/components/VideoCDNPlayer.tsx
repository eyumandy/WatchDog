import React, { useState, useEffect, useRef } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface VideoCDNPlayerProps {
  incidentId: string;
  onError?: (error: string) => void;
  onLoad?: () => void;
}

interface DebugInfo {
  response?: {
    status: number;
    statusText: string;
    headers: Record<string, string>;
  };
  cdnUrl?: string;
  videoError?: {
    error?: number;
    errorMessage?: string;
    networkState: number;
    readyState: number;
    currentSrc: string;
  };
  videoInfo?: {
    duration: number;
    videoWidth: number;
    videoHeight: number;
    readyState: number;
  };
}

const VideoCDNPlayer: React.FC<VideoCDNPlayerProps> = ({ incidentId, onError, onLoad }) => {
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [debugInfo, setDebugInfo] = useState<DebugInfo>({});
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const fetchVideoUrl = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Get the CDN URL from our backend
        const response = await fetch(`http://localhost:5000/video-cdn-url/${incidentId}`);
        const responseInfo = {
          status: response.status,
          statusText: response.statusText,
          headers: Object.fromEntries(response.headers.entries()),
        };
        setDebugInfo(prev => ({ ...prev, response: responseInfo }));

        if (!response.ok) {
          throw new Error(`Failed to fetch video URL: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        setVideoUrl(data.url);
        setDebugInfo(prev => ({ ...prev, cdnUrl: data.url }));
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load video URL';
        setError(errorMessage);
        onError?.(errorMessage);
        console.error('Error fetching video URL:', err);
      }
    };

    if (incidentId) {
      fetchVideoUrl();
    }
  }, [incidentId, onError]);

  const handleVideoError = (e: React.SyntheticEvent<HTMLVideoElement, Event>) => {
    const video = e.currentTarget;
    const errorInfo = {
      error: video.error?.code,
      errorMessage: video.error?.message,
      networkState: video.networkState,
      readyState: video.readyState,
      currentSrc: video.currentSrc,
    };
    setDebugInfo(prev => ({ ...prev, videoError: errorInfo }));
    setError(`Video playback error: ${video.error?.message || 'Unknown error'}`);
    onError?.(`Video playback error: ${video.error?.message || 'Unknown error'}`);
  };

  const handleVideoLoad = () => {
    setIsLoading(false);
    onLoad?.();
    const video = videoRef.current;
    if (video) {
      setDebugInfo(prev => ({
        ...prev,
        videoInfo: {
          duration: video.duration,
          videoWidth: video.videoWidth,
          videoHeight: video.videoHeight,
          readyState: video.readyState,
        }
      }));
    }
  };

  if (isLoading && !videoUrl) {
    return (
      <div className="w-full h-64 bg-black/20 rounded-lg flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription className="flex items-center justify-between">
          <span>{error}</span>
          <button 
            onClick={() => window.location.reload()}
            className="flex items-center gap-2 px-3 py-1 rounded bg-white/10 hover:bg-white/20 transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            Retry
          </button>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      <div className="relative bg-black rounded-lg overflow-hidden min-h-[300px]">
        {videoUrl && (
          <video
            ref={videoRef}
            className="w-full h-full object-contain"
            controls
            controlsList="nodownload"
            onError={handleVideoError}
            onLoadedData={handleVideoLoad}
            onLoadStart={() => setIsLoading(true)}
            crossOrigin="anonymous"
            playsInline
          >
            <source src={videoUrl} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        )}
        {isLoading && videoUrl && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
          </div>
        )}
      </div>
      
      {/* Debug info in development */}
      {process.env.NODE_ENV === 'development' && (
        <div className="mt-4 p-4 bg-gray-900 rounded-lg text-xs text-white/60 space-y-2">
          <p>Incident ID: {incidentId}</p>
          <p>Loading: {isLoading ? 'Yes' : 'No'}</p>
          <p>Error: {error || 'None'}</p>
          <details>
            <summary className="cursor-pointer">Debug Information</summary>
            <pre className="mt-2 whitespace-pre-wrap">
              {JSON.stringify(debugInfo, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
};

export default VideoCDNPlayer;