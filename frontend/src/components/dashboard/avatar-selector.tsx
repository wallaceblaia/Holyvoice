"use client"

import React, { Fragment } from "react"
import { Dialog, Transition } from "@headlessui/react"
import { Button } from "../ui/button"
import { Avatar, AvatarImage } from "../ui/avatar"

// Lista de avatares pré-definidos usando DiceBear
const avatars = Array.from({ length: 12 }, (_, i) => ({
  id: i + 1,
  url: `https://api.dicebear.com/7.x/avataaars/svg?seed=avatar${i + 1}`,
}))

type AvatarSelectorProps = {
  currentAvatar?: string
  onSelect: (avatarUrl: string) => void
}

export function AvatarSelector({ currentAvatar, onSelect }: AvatarSelectorProps) {
  const [isOpen, setIsOpen] = React.useState(false)

  return (
    <>
      <Button variant="outline" onClick={() => setIsOpen(true)}>
        Alterar Avatar
      </Button>

      <Transition appear show={isOpen} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={() => setIsOpen(false)}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-25" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                  <Dialog.Title
                    as="h3"
                    className="text-lg font-medium leading-6 text-gray-900"
                  >
                    Escolha seu Avatar
                  </Dialog.Title>
                  <div className="mt-4 grid grid-cols-4 gap-4">
                    {avatars.map((avatar) => (
                      <button
                        key={avatar.id}
                        className={`rounded-lg p-1 hover:bg-accent ${
                          currentAvatar === avatar.url ? "ring-2 ring-primary" : ""
                        }`}
                        onClick={() => {
                          onSelect(avatar.url)
                          setIsOpen(false)
                        }}
                      >
                        <Avatar className="h-16 w-16">
                          <AvatarImage src={avatar.url} alt={`Avatar ${avatar.id}`} />
                        </Avatar>
                      </button>
                    ))}
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </>
  )
} 