"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  ChevronLeft,
  ChevronDown,
  ChevronRight,
  Home,
  Music2,
  Users,
  Settings,
  Menu as MenuIcon,
  FolderPlus,
  Youtube,
  Video,
  Radio,
  Activity
} from "lucide-react"

const menuItems = [
  {
    title: "Início",
    href: "/dashboard",
    icon: Home,
  },
  {
    title: "Projetos",
    icon: FolderPlus,
    submenu: [
      {
        title: "Vídeo do Youtube",
        href: "/dashboard/projects/youtube",
        icon: Video,
      },
      {
        title: "Live",
        href: "/dashboard/projects/live",
        icon: Radio,
      },
      {
        title: "Monitoramento",
        href: "/dashboard/projects/monitoring",
        icon: Activity,
      }
    ]
  },
  {
    title: "Músicas",
    href: "/dashboard/songs",
    icon: Music2,
  },
  {
    title: "Cadastro",
    icon: FolderPlus,
    submenu: [
      {
        title: "Canais do YouTube",
        href: "/dashboard/youtube/channels",
        icon: Youtube,
      }
    ]
  },
  {
    title: "Usuários",
    href: "/dashboard/users",
    icon: Users,
  },
  {
    title: "Configurações",
    href: "/dashboard/settings",
    icon: Settings,
  },
]

export function SideMenu() {
  const [collapsed, setCollapsed] = useState(false)
  const [openSubmenu, setOpenSubmenu] = useState<string | null>(null)
  const pathname = usePathname()

  const toggleSubmenu = (title: string) => {
    setOpenSubmenu(openSubmenu === title ? null : title)
  }

  return (
    <div
      className={cn(
        "relative h-full border-r bg-background p-4 transition-all duration-300",
        collapsed ? "w-[80px]" : "w-[240px]"
      )}
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className={cn(
          "text-lg font-semibold transition-all duration-300",
          collapsed ? "opacity-0 w-0" : "opacity-100"
        )}>
          HolyVoice
        </h2>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setCollapsed(!collapsed)}
          className="h-8 w-8 ml-auto"
        >
          {collapsed ? <MenuIcon size={18} /> : <ChevronLeft size={18} />}
        </Button>
      </div>

      <ScrollArea className="h-[calc(100vh-8rem)]">
        <div className="space-y-2">
          {menuItems.map((item) => (
            <div key={item.title}>
              {item.submenu ? (
                <>
                  <Button
                    variant="ghost"
                    className={cn(
                      "w-full justify-start",
                      collapsed ? "px-2" : "px-4"
                    )}
                    onClick={() => !collapsed && toggleSubmenu(item.title)}
                  >
                    <item.icon size={20} className="text-muted-foreground" />
                    {!collapsed && (
                      <>
                        <span className="ml-2 flex-1 text-left">{item.title}</span>
                        <ChevronRight
                          size={16}
                          className={cn(
                            "transition-transform",
                            openSubmenu === item.title && "rotate-90"
                          )}
                        />
                      </>
                    )}
                  </Button>
                  {!collapsed && openSubmenu === item.title && (
                    <div className="ml-4 mt-2 space-y-2">
                      {item.submenu.map((subItem) => (
                        <Link key={subItem.href} href={subItem.href}>
                          <Button
                            variant={pathname === subItem.href ? "secondary" : "ghost"}
                            className="w-full justify-start pl-6"
                          >
                            <subItem.icon size={18} className={cn(
                              "transition-colors",
                              pathname === subItem.href 
                                ? "text-primary" 
                                : "text-muted-foreground group-hover:text-primary"
                            )} />
                            <span className="ml-2">{subItem.title}</span>
                          </Button>
                        </Link>
                      ))}
                    </div>
                  )}
                </>
              ) : (
                <Link href={item.href!}>
                  <Button
                    variant={pathname === item.href ? "secondary" : "ghost"}
                    className={cn(
                      "w-full justify-start",
                      collapsed ? "px-2" : "px-4"
                    )}
                  >
                    <item.icon size={20} className={cn(
                      "transition-colors",
                      pathname === item.href 
                        ? "text-primary" 
                        : "text-muted-foreground group-hover:text-primary"
                    )} />
                    <span className={cn(
                      "ml-2 transition-all duration-300",
                      collapsed ? "opacity-0 w-0" : "opacity-100"
                    )}>
                      {item.title}
                    </span>
                  </Button>
                </Link>
              )}
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  )
} 