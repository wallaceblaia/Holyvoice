import { Metadata } from "next"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { UserProfile } from "@/components/dashboard/user-profile"

export const metadata: Metadata = {
  title: "Perfil | HolyVoice",
  description: "Gerencie seu perfil no HolyVoice",
}

export default function ProfilePage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Meu Perfil</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Informações Pessoais</CardTitle>
        </CardHeader>
        <CardContent>
          <UserProfile />
        </CardContent>
      </Card>
    </div>
  )
} 