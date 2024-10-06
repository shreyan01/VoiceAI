"use client"
import { useState } from 'react'
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { Textarea } from "./ui/textarea"
import { Wand2, Upload, Play, Download, Loader2 } from 'lucide-react'

export default function GenerateAudioPage() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [customText, setCustomText] = useState('')
  const [generatedAudioUrl, setGeneratedAudioUrl] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null
    setUploadedFile(file)
  }

  const handleTextChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setCustomText(event.target.value)
  }

  const handleGenerate = async () => {
    if (!uploadedFile || !customText) {
      setError("Please upload a file and enter custom text.")
      return
    }

    // Check if the file still exists and is accessible
    if (!(uploadedFile instanceof File) || uploadedFile.size === 0) {
      setError("The selected file is no longer available. Please select the file again.")
      return
    }

    setIsGenerating(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', uploadedFile)
    formData.append('text', customText)

    try {
      console.log('Sending request to:', 'https://89c7-122-161-52-125.ngrok-free.app/process_audio/')
      const response = await fetch('https://89c7-122-161-52-125.ngrok-free.app/process_audio/', {
        method: 'POST',
        body: formData,
      })

      console.log('Response status:', response.status)
      console.log('Response headers:', Object.fromEntries(response.headers))

      if (!response.ok) {
        const errorText = await response.text()
        console.error('Error response:', errorText)
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }

      const blob = await response.blob()
      console.log('Received blob:', blob)

      if (blob.type !== 'audio/mpeg') {
        console.error('Unexpected content type:', blob.type)
        throw new Error(`Unexpected content type: ${blob.type}`);
      }

      const url = URL.createObjectURL(blob)
      setGeneratedAudioUrl(url)
      console.log('Generated audio URL:', url)
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('Error generating audio:', errorMessage);
      setError(`An error occurred while generating the audio: ${errorMessage}`);
    } finally {
      setIsGenerating(false)
    }
  }

  const handleDownload = () => {
    if (generatedAudioUrl) {
      const link = document.createElement('a')
      link.href = generatedAudioUrl
      link.download = 'generated_audio.mp3'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 to-white">
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Wand2 className="h-8 w-8 text-purple-600" />
            <span className="text-2xl font-bold text-purple-600">VoiceAI</span>
          </div>
        </nav>
      </header>

      <main className="container mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold mb-8 text-center bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-pink-600">
          Generate Your Custom Audio
        </h1>

        <div className="max-w-2xl mx-auto space-y-8">
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-purple-600">1. Upload Your Voice</h2>
            <div className="flex items-center space-x-4">
              <Input
                type="file"
                accept="audio/*,video/*"
                onChange={handleFileUpload}
                className="flex-grow text-black bg-white"
              />
              <Button variant="outline" className="flex items-center space-x-2 text-purple-400">
                <Upload className="h-4 w-4 text-purple-400" />
                <span>Upload</span>
              </Button>
            </div>
            {uploadedFile && (
              <p className="text-sm text-gray-600 dark:text-gray-300">
                Uploaded: {uploadedFile.name}
              </p>
            )}
          </div>

          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-purple-600">2. Enter Your Text</h2>
            <Textarea
              placeholder="Enter the text you want to convert to speech..."
              value={customText}
              onChange={handleTextChange}
              className="w-full h-32 bg-white text-black"
            />
          </div>

          <Button
            onClick={handleGenerate}
            className="w-full bg-purple-600 hover:bg-purple-700 text-white"
            disabled={!uploadedFile || !customText || isGenerating}
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              'Generate Audio'
            )}
          </Button>

          {error && (
            <p className="text-red-500 text-center">{error}</p>
          )}

          {generatedAudioUrl && (
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold text-gray-800 dark:text-white">3. Your Generated Audio</h2>
              <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
                <audio controls className="w-full mb-4">
                  <source src={generatedAudioUrl} type="audio/mpeg" />
                  Your browser does not support the audio element.
                </audio>
                <div className="flex justify-between">
                  <Button 
                    variant="outline" 
                    className="flex items-center space-x-2"
                    onClick={() => document.querySelector('audio')?.play()}
                  >
                    <Play className="h-4 w-4" />
                    <span>Play</span>
                  </Button>
                  <Button 
                    variant="outline" 
                    className="flex items-center space-x-2"
                    onClick={handleDownload}
                  >
                    <Download className="h-4 w-4" />
                    <span>Download</span>
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}