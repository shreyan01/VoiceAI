"use client"

import { Button } from "./components/ui/button"
import { Play, Upload, Wand2 } from 'lucide-react'
import { useRouter } from 'next/navigation'

export default function Component() {

  const router = useRouter()
  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 to-white">
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Wand2 className="h-8 w-8 text-purple-600" />
            <span className="text-2xl font-bold text-purple-600">VoiceAI</span>
          </div>
          <div className="hidden md:flex space-x-4">
            <a href="#features" className="text-gray-600 hover:text-gray-800 ">Features</a>
            <a href="#how-it-works" className="text-gray-600 hover:text-gray-800 ">How It Works</a>
            <a href="#pricing" className="text-gray-600 hover:text-gray-800">Pricing</a>
          </div>
          <Button className="text-purple-400">Sign Up</Button>
        </nav>
      </header>

      <main>
        <section className="container mx-auto px-4 py-16 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-pink-600">
            Your Voice, Amplified by AI
          </h1>
          <p className="text-xl mb-8 text-purple-500">
            Upload your voice, generate custom audio. It's that simple.
          </p>
          <div className="flex flex-col md:flex-row justify-center items-center space-y-4 md:space-y-0 md:space-x-4">
            <Button size="lg" className="bg-purple-600 hover:bg-purple-700" onClick={() => router.push('/generate-audio')}>
              Get Started
            </Button>
            <Button size="lg" variant="outline">
              Learn More
            </Button>
          </div>
        </section>

        <section id="features" className="container mx-auto px-4 py-16">
          <h2 className="text-3xl font-bold mb-8 text-center">Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
              <Upload className="h-12 w-12 text-purple-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Custom Voice Upload</h3>
              <p className="text-gray-600 dark:text-gray-300">Upload your own voice or choose from our library of professional voice actors.</p>
            </div>
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
              <Wand2 className="h-12 w-12 text-purple-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">AI-Powered Generation</h3>
              <p className="text-gray-600 dark:text-gray-300">Our advanced AI models create natural-sounding speech in your chosen voice.</p>
            </div>
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
              <Play className="h-12 w-12 text-purple-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Instant Playback</h3>
              <p className="text-gray-600 dark:text-gray-300">Listen to your generated audio instantly and make adjustments in real-time.</p>
            </div>
          </div>
        </section>
        
        <section className="container mx-auto px-4 py-16">
          <h2 className="text-3xl font-bold mb-8 text-center">What Our Users Say</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
              <p className="text-gray-600 dark:text-gray-300 mb-4">"VoiceAI has revolutionized my workflow. I can now create professional voiceovers in minutes!"</p>
              <p className="font-semibold">- Sarah J., Content Creator</p>
            </div>
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
              <p className="text-gray-600 dark:text-gray-300 mb-4">"The quality of the generated audio is incredible. It's hard to tell it apart from a real recording."</p>
              <p className="font-semibold">- Mark T., Podcast Host</p>
            </div>
          </div>
        </section>

        <section id="pricing" className="container mx-auto px-4 py-16">
          <h2 className="text-3xl font-bold mb-8 text-center">Pricing Plans</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
              <h3 className="text-xl font-semibold mb-2">Basic</h3>
              <p className="text-3xl font-bold mb-4">$9.99<span className="text-sm font-normal">/month</span></p>
              <ul className="mb-6 space-y-2">
                <li>100 minutes of audio generation</li>
                <li>5 custom voice uploads</li>
                <li>Standard support</li>
              </ul>
              <Button className="w-full">Choose Plan</Button>
            </div>
            <div className="bg-purple-600 text-white p-6 rounded-lg shadow-lg transform scale-105">
              <h3 className="text-xl font-semibold mb-2">Pro</h3>
              <p className="text-3xl font-bold mb-4">$24.99<span className="text-sm font-normal">/month</span></p>
              <ul className="mb-6 space-y-2">
                <li>500 minutes of audio generation</li>
                <li>20 custom voice uploads</li>
                <li>Priority support</li>
                <li>Advanced voice editing tools</li>
              </ul>
              <Button className="w-full bg-white text-purple-600 hover:bg-gray-100">Choose Plan</Button>
            </div>
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
              <h3 className="text-xl font-semibold mb-2">Enterprise</h3>
              <p className="text-3xl font-bold mb-4">Custom</p>
              <ul className="mb-6 space-y-2">
                <li>Unlimited audio generation</li>
                <li>Unlimited custom voice uploads</li>
                <li>24/7 premium support</li>
                <li>API access</li>
                <li>Custom integrations</li>
              </ul>
              <Button className="w-full">Contact Sales</Button>
            </div>
          </div>
        </section>
      </main>

      <footer className="bg-gray-100 dark:bg-gray-900">
        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div>
              <h4 className="text-lg font-semibold mb-4">Product</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">Features</a></li>
                <li><a href="#" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">Pricing</a></li>
                <li><a href="#" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">FAQ</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Company</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">About</a></li>
                <li><a href="#" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">Blog</a></li>
                <li><a href="#" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">Careers</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Resources</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">Documentation</a></li>
                <li><a href="#" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">Tutorials</a></li>
                <li><a href="#" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">Support</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Legal</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">Privacy Policy</a></li>
                <li><a href="#" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">Terms of Service</a></li>
                <li><a href="#" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">Cookie Policy</a></li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
            <p className="text-center text-gray-500 dark:text-gray-400">&copy; 2023 VoiceAI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}