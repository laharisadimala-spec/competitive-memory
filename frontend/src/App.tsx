import React, { useEffect, useState } from 'react'
import { Brain, Search, TrendingUp, Users, Wifi } from 'lucide-react'
import { api } from './services/api'
import * as Types from './types'
import Timeline from './components/Timeline'
import Strategy from './components/Strategy'
import Investigation from './components/Investigation'
import WarRoom from './components/WarRoom'
import MemoryExplorer from './components/MemoryExplorer'
import TimeMachine from './components/TimeMachine'
import MemoryAssistant from './components/MemoryAssistant'
import './styles/globals.css'

export default function App() {
  const [currentTab, setCurrentTab] = useState('timeline')
  const [competitors, setCompetitors] = useState<Types.Competitor[]>([])
  const [selectedCompetitor, setSelectedCompetitor] = useState('')
  const [memoryStatus, setMemoryStatus] = useState<Types.MemoryStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    initializeApp()
  }, [])

  async function initializeApp() {
    try {
      const [competitorsData, statusData] = await Promise.all([
        api.getCompetitors(),
        api.getMemoryStatus()
      ])
      setCompetitors(competitorsData.competitors)
      setMemoryStatus(statusData)
      if (competitorsData.competitors.length > 0) {
        setSelectedCompetitor(competitorsData.competitors[0].name)
      }
    } catch (error) {
      console.error('Failed to load app:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg">
            <Brain size={34} />
          </div>
          <p className="text-lg font-semibold text-slate-800">Loading Competitive Memory</p>
          <p className="mt-1 text-sm text-slate-500">Restoring competitive context...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur shadow-sm">
        <div className="mx-auto max-w-7xl px-6 py-5">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-600 text-white shadow-md">
                <Brain size={26} />
              </div>
              <div>
                <div className="flex items-center gap-3">
                  <h1 className="text-2xl font-bold tracking-tight text-slate-900">Competitive Memory</h1>
                  <span className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700">v1.0</span>
                </div>
                <p className="mt-1 text-sm text-slate-500">Remember every move. Understand the pattern.</p>
              </div>
            </div>
            <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
              <span className={`flex h-8 w-8 items-center justify-center rounded-lg ${memoryStatus?.connected ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                <Wifi size={16} />
              </span>
              <div>
                <p className="text-sm font-semibold text-slate-800">{memoryStatus?.mode || 'Memory status unavailable'}</p>
                <p className="text-xs text-slate-500">{competitors.length} competitors tracked</p>
              </div>
            </div>
          </div>

          <nav className="mt-5 flex gap-2 overflow-x-auto pb-1">
            <TabButton icon={<TrendingUp size={17} />} label="Timeline" active={currentTab === 'timeline'} onClick={() => setCurrentTab('timeline')} />
            <TabButton icon={<Brain size={17} />} label="Strategy" active={currentTab === 'strategy'} onClick={() => setCurrentTab('strategy')} />
            <TabButton icon={<Search size={17} />} label="Investigate" active={currentTab === 'investigate'} onClick={() => setCurrentTab('investigate')} />
            <TabButton icon={<Users size={17} />} label="War Room" active={currentTab === 'warroom'} onClick={() => setCurrentTab('warroom')} />
            <TabButton icon={<ClockIcon />} label="Time Machine" active={currentTab === 'time'} onClick={() => setCurrentTab('time')} />
            <TabButton icon={<MessageIcon />} label="Ask Memory" active={currentTab === 'ask'} onClick={() => setCurrentTab('ask')} />
            <TabButton icon={<Brain size={17} />} label="Memory" active={currentTab === 'memory'} onClick={() => setCurrentTab('memory')} />
          </nav>
        </div>
      </header>

      {competitors.length > 0 && (
        <section className="border-b border-slate-200 bg-white">
          <div className="mx-auto max-w-7xl px-6 py-4">
            <p className="mb-3 text-xs font-bold uppercase tracking-wider text-slate-500">Track competitor</p>
            <div className="flex gap-2 overflow-x-auto">
              {competitors.map(comp => (
                <button
                  key={comp.id}
                  onClick={() => setSelectedCompetitor(comp.name)}
                  className={`rounded-lg px-4 py-2.5 text-sm font-semibold transition ${selectedCompetitor === comp.name ? 'bg-blue-600 text-white shadow-sm' : 'border border-slate-200 bg-white text-slate-700 hover:border-blue-300 hover:bg-blue-50'}`}
                >
                  {comp.name}
                </button>
              ))}
            </div>
          </div>
        </section>
      )}

      <main className="mx-auto max-w-7xl px-6 py-8">
        {currentTab === 'timeline' && <Timeline competitor={selectedCompetitor} />}
        {currentTab === 'strategy' && <Strategy competitor={selectedCompetitor} />}
        {currentTab === 'investigate' && <Investigation competitor={selectedCompetitor} />}
        {currentTab === 'warroom' && <WarRoom />}
        {currentTab === 'time' && <TimeMachine competitor={selectedCompetitor} />}
        {currentTab === 'ask' && <MemoryAssistant competitor={selectedCompetitor} />}
        {currentTab === 'memory' && <MemoryExplorer competitor={selectedCompetitor} />}
      </main>

      <footer className="mt-10 border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-6 text-center text-sm text-slate-500">
          <span className="font-semibold text-slate-700">Competitive Memory</span> · Persistent competitive intelligence powered by memory
        </div>
      </footer>
    </div>
  )
}

function TabButton({ icon, label, active, onClick }: { icon: React.ReactNode; label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`flex shrink-0 items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-semibold transition ${active ? 'bg-blue-600 text-white shadow-sm' : 'border border-slate-200 bg-white text-slate-600 hover:border-blue-300 hover:bg-blue-50 hover:text-blue-700'}`}
    >
      {icon}
      {label}
    </button>
  )
}

function ClockIcon(){ return <span className="text-base">⏳</span> }
function MessageIcon(){ return <span className="text-base">💬</span> }
