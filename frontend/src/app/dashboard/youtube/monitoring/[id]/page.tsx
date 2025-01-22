"use client"

import * as React from "react"
import { MonitoringDetails } from "@/components/monitoring/monitoring-details"

interface MonitoringPageProps {
  params: {
    id: string
  }
}

export default function MonitoringPage({ params }: MonitoringPageProps) {
  return (
    <div className="container py-6">
      <MonitoringDetails monitoringId={parseInt(params.id)} />
    </div>
  )
} 