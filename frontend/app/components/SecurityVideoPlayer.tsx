import React, { useState, useRef, useEffect } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

export interface SecurityVideoPlayerProps {
  videoPath: string | null;
}

const SecurityVideoPlayer: React.FC<SecurityVideoPlayerProps> = ({ videoPath }) => {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const videoRef = useRef<HTMLVideoElement>(null);
  const retryCount = useRef(0);
  const maxRetries = 3;

  const getFullVideoUrl = (path: string | null): string | null => {
    if (!path) return null;
    // Add cache busting parameter to prevent caching issues
    const cacheBuster = `?t=${Date.now()}`;
    const baseUrl = path.startsWith('http') ? path : `http://localhost:5000${path}`;
    return `${baseUrl}${cacheBuster}`;
  };

  useEffect(() => {
    // Reset states when video path changes
    setIsLoading(true);
    setError(null);
    retryCount.current = 0;
    
    // Log the video path for debugging
    console.log('Video path changed:', videoPath);
    console.log('Full video URL:', getFullVideoUrl(videoPath));
  }, [videoPath]);

  const handleVideoError = (e: React.SyntheticEvent<HTMLVideoElement, Event>) => {
    const video = e.target as HTMLVideoElement;
    console.error('Video Error Details:', {
      errorCode: video.error?.code,
      errorMessage: video.error?.message,
      networkState: video.networkState,
      readyState: video.readyState,
      currentSrc: video.currentSrc,
      videoWidth: video.videoWidth,
      videoHeight: video.videoHeight
    });

    // Attempt retry if under max retries
    if (retryCount.current < maxRetries) {
      retryCount.current += 1;
      console.log(`Retrying video load (${retryCount.current}/${maxRetries})...`);
      setTimeout(() => {
        if (videoRef.current) {
          const newUrl = getFullVideoUrl(videoPath);
          console.log('Retrying with URL:', newUrl);
          videoRef.current.src = newUrl || '';
          videoRef.current.load();
        }
      }, 1000);
    } else {
      setError(`Failed to load video (${video.error?.message || 'Unknown error'})`);
      setIsLoading(false);
    }
  };

  const handleVideoLoad = () => {
    console.log('Video loaded successfully');
    setIsLoading(false);
    setError(null);
  };

  const handleLoadStart = () => {
    console.log('Video load started');
    setIsLoading(true);
    setError(null);
  };

  const handleRetry = () => {
    console.log('Manual retry initiated');
    setIsLoading(true);
    setError(null);
    retryCount.current = 0;
    
    if (videoRef.current) {
      const newUrl = getFullVideoUrl(videoPath);
      console.log('Retrying with new URL:', newUrl);
      videoRef.current.src = newUrl || '';
      videoRef.current.load();
    }
  };

  if (!videoPath) {
    return (
      <div className="w-full h-64 bg-black/20 rounded-lg flex items-center justify-center">
        <p className="text-white/60">No video available</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="flex items-center justify-between">
            <span>{error}</span>
            <button 
              onClick={handleRetry}
              className="flex items-center gap-2 px-3 py-1 rounded bg-white/10 hover:bg-white/20 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              Retry
            </button>
          </AlertDescription>
        </Alert>
      )}
      
      <div className="relative bg-black rounded-lg overflow-hidden min-h-[300px]">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
          </div>
        )}
        
        <video
          ref={videoRef}
          className="w-full h-full object-contain"
          controls
          controlsList="nodownload"
          onError={handleVideoError}
          onLoadStart={handleLoadStart}
          onLoadedData={handleVideoLoad}
          preload="metadata"
          playsInline
        >
          <source 
            src={getFullVideoUrl(videoPath) || undefined} 
            type="video/mp4"
          />
          Your browser does not support the video tag.
        </video>
      </div>

      {/* Debug info in development */}
      {process.env.NODE_ENV === 'development' && (
        <div className="mt-4 p-4 bg-gray-900 rounded-lg text-xs text-white/60">
          <p>Video Path: {videoPath}</p>
          <p>Full URL: {getFullVideoUrl(videoPath)}</p>
          <p>Retry Count: {retryCount.current}/{maxRetries}</p>
          <p>Loading: {isLoading ? 'Yes' : 'No'}</p>
          <p>Error: {error || 'None'}</p>
        </div>
      )}
    </div>
  );
};

export default SecurityVideoPlayer;