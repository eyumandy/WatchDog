import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import axios from 'axios';
import { AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface IncidentDetails {
  incident_id: string;
  upload_date: string;
  video_path: string;
  faces: string[];
}

interface SecurityLogDetailsProps {
  selectedLogId: string | null;
}

const SecurityLogDetails: React.FC<SecurityLogDetailsProps> = ({ selectedLogId }) => {
  const [incidentDetails, setIncidentDetails] = useState<IncidentDetails | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchIncidentDetails = async () => {
      if (!selectedLogId) {
        setIncidentDetails(null);
        return;
      }

      setIsLoading(true);
      setError(null);
      
      try {
        const response = await axios.get(`http://localhost:5000/incident/${selectedLogId}`);
        setIncidentDetails(response.data);
      } catch (error) {
        setError('Failed to load incident details');
      } finally {
        setIsLoading(false);
      }
    };

    fetchIncidentDetails();
  }, [selectedLogId]);

  if (!selectedLogId) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-white/60">Select a log entry to view details</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  if (!incidentDetails) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-white/60">No details available</p>
      </div>
    );
  }

  return (
    <motion.div
      key={incidentDetails.incident_id}
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.3 }}
      className="space-y-6 h-full"
    >
      {/* Header */}
      <div>
        <h2 className="text-2xl font-light">Incident Details</h2>
        <p className="text-white/80">Incident ID: {incidentDetails.incident_id}</p>
        <p className="text-white/60">
          Upload Time: {format(new Date(incidentDetails.upload_date), "MMMM d, yyyy HH:mm:ss")}
        </p>
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Video Section - Placeholder */}
        <div className="bg-black/40 rounded-lg overflow-hidden aspect-video flex items-center justify-center">
          <p className="text-white/60">Video loading has been temporarily disabled</p>
        </div>

        {/* Detected Faces */}
        <div className="bg-white/5 rounded-lg p-6 flex flex-col space-y-4">
          <h3 className="text-lg font-medium flex items-center gap-2">
            Detected Faces
            <span className="text-sm font-normal text-white/60">
              ({incidentDetails.faces.length} detected)
            </span>
          </h3>
          
          {incidentDetails.faces && incidentDetails.faces.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {incidentDetails.faces.map((face, index) => (
                <div key={face} className="flex flex-col space-y-2">
                  <div className="aspect-square bg-black/40 rounded-lg overflow-hidden relative group">
                    <img
                      src={`http://localhost:5000${face}`}
                      alt={`Person ${index + 1}`}
                      className="w-full h-full object-cover transition-transform duration-200 group-hover:scale-105"
                      loading="lazy"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                  </div>
                  <p className="text-sm text-white/80 text-center">Person {index + 1}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-32">
              <p className="text-white/60">No faces detected in this incident</p>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default SecurityLogDetails;