"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bell, Camera, Server, AlertTriangle, User, DoorClosed, Clock } from "lucide-react";
import axios from "axios";

interface Incident {
  incident_id: string;
  upload_date: string;
}

const getRandomIcon = () => {
  const icons = [
    <AlertTriangle size={16} className="text-yellow-400" />,
    <Camera size={16} className="text-blue-400" />,
    <Server size={16} className="text-green-400" />,
    <User size={16} className="text-purple-400" />,
    <DoorClosed size={16} className="text-red-400" />,
    <Clock size={16} className="text-indigo-400" />,
    <Bell size={16} className="text-white/60" />,
  ];
  return icons[Math.floor(Math.random() * icons.length)];
};

export default function RecentActivity() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [showFilters, setShowFilters] = useState(false);

  // Fetch incidents function
  const fetchIncidents = async () => {
    try {
      const response = await axios.get("http://localhost:5000/incidents");
      setIncidents(response.data.incidents);
    } catch (error) {
      console.error("Error fetching incidents:", error);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchIncidents();

    // Set interval to fetch data every 15 seconds
    const interval = setInterval(() => {
      console.log("Refreshing incidents data...");
      fetchIncidents();
    }, 15000);

    // Cleanup interval on component unmount
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="bg-white/5 backdrop-blur-md rounded-2xl p-6 border border-white/10 h-full"
    >
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-light">Recent Activity</h2>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="p-2 bg-white/10 rounded-full hover:bg-white/20 transition-colors"
        >
          <Bell size={16} />
        </button>
      </div>
      <div className="space-y-4 overflow-y-auto max-h-[calc(100vh-16rem)]">
        <AnimatePresence initial={false}>
          {incidents.map((incident) => (
            <motion.div
              key={incident.incident_id}
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.3 }}
              className="flex items-start space-x-3 bg-white/5 rounded-lg p-3"
            >
              <div className="mt-1">{getRandomIcon()}</div>
              <div className="flex-grow">
                <p className="text-sm text-white/80">{incident.incident_id}</p>
                <p className="text-xs text-white/60">
                  Time: {new Date(incident.upload_date).toLocaleString()}
                </p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
