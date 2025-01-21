import { Metadata } from "next"
import { SideMenu } from "@/components/dashboard/side-menu"
import { Header } from "@/components/dashboard/header"

export const metadata: Metadata = {
  title: "Dashboard - HolyVoice",
  description: "Painel de controle do HolyVoice",
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex h-screen">
      <SideMenu />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 overflow-y-auto bg-muted/10 p-6">
          <div className="max-w-[1200px] mx-auto w-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
} 