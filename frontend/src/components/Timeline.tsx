import React, { useEffect, useState } from 'react'
import { Calendar, ChevronRight, Clock3 } from 'lucide-react'
import { api } from '../services/api'
import * as Types from '../types'

const icons: Record<string, string> = { hiring: '👥', product_launch: '🚀', feature_release: '✨', pricing_change: '💰', partnership: '🤝', funding: '💵', leadership_change: '👔', messaging_shift: '📢', website_change: '🌐', market_event: '📈', acquisition: '🎯', strategy_shift: '🔄' }

export default function Timeline({ competitor }: { competitor: string }) {
  const [events, setEvents] = useState<Types.CompetitorEvent[]>([])
  const [days, setDays] = useState(180)
  const [type, setType] = useState('')
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState<Types.CompetitorEvent | null>(null)

  useEffect(() => { load() }, [competitor, days, type])
  async function load() {
    setLoading(true)
    try { const data = await api.getTimeline(competitor, days); setEvents(type ? (data.events || []).filter((e: Types.CompetitorEvent) => e.event_type === type) : data.events || []) }
    catch (e) { console.error(e) } finally { setLoading(false) }
  }

  return <div className="space-y-6">
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div><div className="flex items-center gap-2 text-slate-900 font-bold"><Calendar size={18} className="text-blue-600"/> Competitive timeline</div><p className="mt-1 text-sm text-slate-500">See what happened, in order, and trace the signals behind a change.</p></div>
        <div className="flex flex-wrap gap-2">{[30,60,90,180].map(d => <button key={d} onClick={() => setDays(d)} className={`rounded-lg px-3 py-2 text-xs font-semibold ${days===d?'bg-blue-600 text-white':'border border-slate-200 bg-white text-slate-600 hover:bg-blue-50'}`}>{d} days</button>)}</div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2"><button onClick={() => setType('')} className={`rounded-full px-3 py-1.5 text-xs font-semibold ${!type?'bg-slate-900 text-white':'bg-slate-100 text-slate-600'}`}>All events</button>{Object.keys(icons).slice(0,8).map(t=><button key={t} onClick={()=>setType(t)} className={`rounded-full px-3 py-1.5 text-xs font-semibold ${type===t?'bg-blue-100 text-blue-700':'bg-slate-100 text-slate-600'}`}>{t.replaceAll('_',' ')}</button>)}</div>
    </div>
    {loading ? <Loading label="Loading competitive history…"/> : <div className="relative space-y-3">{events.map((event) => <button key={event.id} onClick={()=>setSelected(event)} className="group relative block w-full text-left pl-10"><span className="absolute left-2 top-5 h-3 w-3 rounded-full bg-blue-600 ring-4 ring-blue-50"/><span className="absolute left-[7px] top-8 bottom-[-16px] w-px bg-slate-200 last:hidden"/><div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm hover:border-blue-200 hover:shadow-md"><div className="flex items-start gap-4"><span className="text-2xl">{icons[event.event_type] || '📌'}</span><div className="min-w-0 flex-1"><div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between"><div><p className="font-bold text-slate-900">{event.title}</p><p className="mt-1 text-sm leading-6 text-slate-600">{event.description}</p></div><span className="inline-flex shrink-0 items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600"><Clock3 size={12}/>{new Date(event.date).toLocaleDateString()}</span></div><div className="mt-3 flex flex-wrap gap-2">{event.entities.slice(0,4).map(x=><span key={x} className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">{x}</span>)}</div></div><ChevronRight className="mt-1 text-slate-300 group-hover:text-blue-600" size={18}/></div></div></button>)}</div>}
    {selected && <div className="fixed inset-0 z-[70] flex items-center justify-center bg-slate-900/30 p-4" onClick={()=>setSelected(null)}><div className="w-full max-w-2xl rounded-2xl bg-white p-6 shadow-2xl" onClick={e=>e.stopPropagation()}><div className="flex items-start justify-between"><div><p className="text-xs font-bold uppercase tracking-wider text-blue-600">Observed event</p><h3 className="mt-1 text-xl font-bold text-slate-900">{selected.title}</h3></div><button onClick={()=>setSelected(null)} className="text-slate-400 hover:text-slate-700">✕</button></div><p className="mt-4 leading-7 text-slate-600">{selected.description}</p><div className="mt-5 grid gap-3 sm:grid-cols-3"><Info label="Date" value={new Date(selected.date).toLocaleDateString()}/><Info label="Type" value={selected.event_type.replaceAll('_',' ')}/><Info label="Importance" value={selected.importance}/></div>{selected.outcome && <div className="mt-4 rounded-xl bg-emerald-50 p-4 text-sm text-emerald-800"><b>Outcome:</b> {selected.outcome}</div>}</div></div>}
  </div>
}
function Info({label,value}:{label:string,value:string}){return <div className="rounded-xl bg-slate-50 p-3"><p className="text-xs font-semibold text-slate-500">{label}</p><p className="mt-1 text-sm font-bold capitalize text-slate-900">{value}</p></div>}
function Loading({label}:{label:string}){return <div className="rounded-2xl border border-slate-200 bg-white p-12 text-center shadow-sm"><div className="mx-auto h-9 w-9 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600"/><p className="mt-4 font-medium text-slate-600">{label}</p></div>}
