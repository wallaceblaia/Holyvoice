import { Metadata } from "next"
import { MonitoringDetails } from "@/components/monitoring/monitoring-details"

export const metadata: Metadata = {
  title: "Detalhes do Monitoramento",
  description: "Visualize os detalhes e status do monitoramento"
}

export default async function MonitoringDetailsPage({ params }: { params: { id: string } }) {
  const monitoringId = await Promise.resolve(parseInt(params.id))

  return (
    <div className="flex flex-col gap-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Detalhes do Monitoramento</h1>
      </div>
      <div className="grid gap-4">
        <MonitoringDetails monitoringId={monitoringId} />
      </div>
    </div>
  )
} 