"use client";

import React from "react";
import AnalyticalDashboard from "@/components/dashboard/AnalyticalDashboard";
import { motion } from "framer-motion";

export default function AnalysisPage() {
  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen bg-background"
    >
      <AnalyticalDashboard />
    </motion.div>
  );
}
