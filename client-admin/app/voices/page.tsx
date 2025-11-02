'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/store'
import { voicesAPI } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function VoicesPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const [voices, setVoices] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }

    const loadVoices = async () => {
      try {
        const data = await voicesAPI.list()
        setVoices(data)
      } catch (error) {
        console.error('Failed to load voices:', error)
      } finally {
        setLoading(false)
      }
    }

    loadVoices()
  }, [isAuthenticated, router])

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6 flex justify-between items-center">
          <h2 className="text-3xl font-bold">Voices</h2>
          <Button>Add Voice</Button>
        </div>

        {loading ? (
          <div>Loading...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {voices.map((voice) => (
              <Card key={voice.id}>
                <CardHeader>
                  <CardTitle>{voice.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">
                    Provider: {voice.provider} / Language: {voice.language}
                  </p>
                  <p className="text-sm mt-2">
                    Status: {voice.is_active ? 'Active' : 'Inactive'}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

