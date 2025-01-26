/**
 * EventList Component
 *
 * This component dynamically displays a chronological list of security events fetched from the backend.
 * Each event includes an icon, description, and timestamp.
 *
 * Features:
 * - Event type indicators
 * - Timestamp formatting
 * - Animated transitions
 * - Automatic refresh every 15 seconds
 */

"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { AlertCircle, Video, Server, User, DoorClosed, Clock } from "lucide-react";
import axios from "axios";
import { formatDistanceToNow } from "date-fns";

interface Event {
  id: string; // Unique incident ID
  description: string; // Incident description
  timestamp: string; // Time the incident occurred
  type: "alert" | "camera" | "system" | "user" | "door" | "schedule"; // Randomized event type for the icon
}

const getEventIcon = (type: Event["type"]) => {
  switch (type) {
    case "alert":
      return <AlertCircle size={16} className="text-red-400" />;
    case "camera":
      return <Video size={16} className="text-blue-400" />;
    case "system":
      return <Server size={16} className="text-green-400" />;
    case "user":
      return <User size={16} className="text-purple-400" />;
    case "door":
      return <DoorClosed size={16} className="text-yellow-400" />;
    case "schedule":
      return <Clock size={16} className="text-indigo-400" />;
    default:
      return <AlertCircle size={16} className="text-white/60" />;
  }
};

const getRandomEventType = (): Event["type"] => {
  const types: Event["type"][] = ["alert", "camera", "system", "user", "door", "schedule"];
  return types[Math.floor(Math.random() * types.length)];
};

export default function EventList() {
  const [events, setEvents] = useState<Event[]>([]);

  // Fetch incidents from the backend
  const fetchEvents = async () => {
    try {
      const response = await axios.get("http://localhost:5000/incidents");
      const incidents = response.data.incidents.map((incident: any) => ({
        id: incident.incident_id,
        description: `${incident.incident_id}`, // Description derived from incident ID
        timestamp: incident.upload_date,
        type: getRandomEventType(), // Assign a random event type for the icon
      }));
      setEvents(incidents);
    } catch (error) {
      console.error("Error fetching events:", error);
    }
  };

  // Fetch data initially and refresh every 15 seconds
  useEffect(() => {
    fetchEvents(); // Initial fetch
    const interval = setInterval(() => {
      console.log("Refreshing events...");
      fetchEvents();
    }, 15000);

    return () => clearInterval(interval); // Cleanup interval on component unmount
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="space-y-4"
    >
      {events.map((event) => (
        <motion.div
          key={event.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
          className="bg-white/5 backdrop-blur-md rounded-lg p-4 flex items-center space-x-4 border border-white/10"
        >
          <div className="flex-shrink-0">{getEventIcon(event.type)}</div>
          <div className="flex-grow">
            <p className="text-sm text-white/80">{event.description}</p>
            <p className="text-xs text-white/60">
              {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
            </p>
          </div>
        </motion.div>
      ))}
    </motion.div>
  );
}
