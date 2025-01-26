"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import { format } from "date-fns";
import axios from "axios";

// Interface to define the structure of incident details
interface SecurityLogDetailsProps {
  selectedLogId: string | null; // ID of the selected log entry
}

interface IncidentDetails {
  incident_id: string; // Unique identifier for the incident
  upload_date: string; // Timestamp of when the incident was uploaded
  video_path: string;  // URL for the incident video
  faces: string[];     // Array of URLs for detected face images
}

export default function SecurityLogDetails({ selectedLogId }: SecurityLogDetailsProps) {
  const [incidentDetails, setIncidentDetails] = useState<IncidentDetails | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Fetch incident details whenever a new log is selected
  useEffect(() => {
    if (!selectedLogId) {
      setIncidentDetails(null); // Reset details if no log is selected
      return;
    }

    const fetchIncidentDetails = async () => {
      try {
        // Make API call to get incident details
        const response = await axios.get(`http://localhost:5000/incident/${selectedLogId}`);
        setIncidentDetails(response.data); // Update state with incident details
      } catch (error) {
        console.error("Error fetching incident details:", error);
      }
    };

    fetchIncidentDetails();
  }, [selectedLogId]);

  // Fallback UI when no log is selected
  if (!selectedLogId || !incidentDetails) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
        className="flex items-center justify-center h-full"
      >
        <p className="text-white/60">Select a log entry to view details</p>
      </motion.div>
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
      <div>
        <h2 className="text-2xl font-light">Incident Details</h2>
        <p className="text-white/80">Incident ID: {incidentDetails.incident_id}</p>
        <p className="text-white/60">
          Upload Time: {format(new Date(incidentDetails.upload_date), "MMMM d, yyyy HH:mm:ss")}
        </p>
      </div>

      {/* Video and Faces Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Video Player */}
        <div className="relative bg-black rounded-lg overflow-hidden">
          {/* Render the video if the path exists */}
          {incidentDetails.video_path ? (
            <video
              ref={videoRef}
              src={incidentDetails.video_path}
              controls
              className="w-full h-[300px] lg:h-full object-cover bg-black"
            />
          ) : (
            <p className="text-white/60">Video not available for this incident.</p>
          )}
        </div>

        {/* Detected Faces */}
        {incidentDetails.faces.length > 0 && (
          <div className="bg-white/5 rounded-lg p-4 flex flex-col space-y-4">
            <h3 className="text-lg font-medium">Detected Faces</h3>
            <div className="grid grid-cols-3 gap-4">
              {incidentDetails.faces.map((face, index) => (
                <Image
                  key={index}
                  src={face}
                  alt={`Face ${index + 1}`}
                  width={100}
                  height={100}
                  className="rounded-lg object-cover bg-black"
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
