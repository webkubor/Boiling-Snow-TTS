import { useEffect, useMemo, useState } from 'react'
import { Card } from './components/ui/card'
import { Button } from './components/ui/button'

const defaultLine = { role: '', text: '', tone: '', emotion: '', emotion_priority: false }

export default function App() {
  const [personas, setPersonas] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [message, setMessage] = useState('')

  const [mode, setMode] = useState('clone')
  const [modelSize, setModelSize] = useState('1.7B')
  const [persona, setPersona] = useState('')
  const [voiceName, setVoiceName] = useState('')
  const [commitToTemp, setCommitToTemp] = useState(false)
  const [referenceAudio, setReferenceAudio] = useState('')
  const [title, setTitle] = useState('WebUI实时生成')
  const [episode, setEpisode] = useState('WEB')
  const [text, setText] = useState('')
  const [tone, setTone] = useState('')
  const [emotion, setEmotion] = useState('')
  const [emotionPriority, setEmotionPriority] = useState(false)
  const [lines, setLines] = useState([{ ...defaultLine }])

  useEffect(() => {
    fetch('/api/personas')
      .then((res) => res.json())
      .then((data) => {
        const items = data.items || []
        setPersonas(items)
        if (items[0] && !persona) setPersona(items[0].key)
      })
      .catch((err) => setMessage(`加载角色失败: ${String(err)}`))
  }, [])

  const personaOptions = useMemo(
    () => personas.map((p) => ({ value: p.key, label: `${p.name} (${p.key})` })),
    [personas]
  )

  const onUploadReference = async (event) => {
    const file = event.target.files?.[0]
    if (!file || !persona) return

    try {
      setUploading(true)
      setMessage('')
      const form = new FormData()
      form.append('persona', persona)
      form.append('file', file)

      const res = await fetch('/api/reference/upload', {
        method: 'POST',
        body: form
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || '上传失败')
      setMessage(`上传并提取成功: ${data.seed_path}`)
    } catch (err) {
      setMessage(`上传失败: ${String(err)}`)
    } finally {
      setUploading(false)
      event.target.value = ''
    }
  }

  const addLine = () => setLines((prev) => [...prev, { ...defaultLine }])
  const removeLine = (idx) => setLines((prev) => prev.filter((_, i) => i !== idx))
  const updateLine = (idx, key, value) => {
    setLines((prev) => prev.map((line, i) => (i === idx ? { ...line, [key]: value } : line)))
  }

  const onGenerate = async () => {
    try {
      setLoading(true)
      setResult(null)
      setMessage('')

      const payload = {
        mode,
        model_size: modelSize,
        persona: mode === 'design' ? '' : persona,
        voice_name: voiceName,
        commit_to_temp: mode === 'design' ? commitToTemp : false,
        reference_audio: mode === 'clone' ? referenceAudio : '',
        title,
        episode,
        text,
        tone,
        emotion,
        emotion_priority: emotionPriority,
        lines
      }

      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || '生成失败')
      setResult(data)
      setMessage(
        data.pending_commit
          ? `设计完成: ${data.path}（仅预览，未落库）。确认满意后勾选“确认落库到temp”再生成一次。`
          : data.generation_json
            ? `生成完成: ${data.path} | 标准样音: ${data.temp_seed_path || 'assets/temp'} | 生成配置: ${data.generation_json}`
            : `生成完成: ${data.path}`
      )
    } catch (err) {
      setMessage(`生成失败: ${String(err)}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto w-full max-w-6xl px-4 py-8 font-body">
      <header className="mb-6 rounded-3xl border border-amber-200/70 bg-amber-50/70 p-6 shadow-flame backdrop-blur">
        <p className="text-xs font-bold uppercase tracking-[0.22em] text-amber-700">Boiling-Snow Control Room</p>
        <h1 className="mt-2 font-title text-4xl text-amber-900">武侠语音控制台</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-amber-900/80">
          支持参考音频上传、单人克隆、音色设计、对话生成与结果试听下载。
        </p>
      </header>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="基础设置" subtitle="模式与参数">
          <div className="grid gap-3 md:grid-cols-2">
            <div>
              <label className="label">模式</label>
              <select className="input" value={mode} onChange={(e) => setMode(e.target.value)}>
                <option value="clone">声音克隆</option>
                <option value="design">音色设计</option>
                <option value="dialogue">对话模式</option>
              </select>
            </div>
            <div>
              <label className="label">模型规格</label>
              <select className="input" value={modelSize} onChange={(e) => setModelSize(e.target.value)}>
                <option value="1.7B">1.7B</option>
                <option value="0.6B">0.6B</option>
              </select>
            </div>
            {mode !== 'design' && (
              <div>
                <label className="label">角色</label>
                <input
                  className="input"
                  list="persona-options"
                  value={persona}
                  onChange={(e) => setPersona(e.target.value)}
                  placeholder="可输入新角色（0-1阶段无需先注册）"
                />
                <datalist id="persona-options">
                  {personaOptions.map((opt) => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </datalist>
              </div>
            )}
            {mode === 'clone' && (
              <>
                <div>
                  <label className="label">上传参考音频</label>
                  <input className="input" type="file" accept=".wav,.mp3,.m4a,.flac,.ogg,.aac" onChange={onUploadReference} disabled={uploading} />
                </div>
                <div className="md:col-span-2">
                  <label className="label">原始参考路径（可选）</label>
                  <input
                    className="input"
                    value={referenceAudio}
                    onChange={(e) => setReferenceAudio(e.target.value)}
                    placeholder="例如：assets/reference/新角色_参考.wav（用于0-1克隆阶段）"
                  />
                </div>
              </>
            )}
            {mode === 'design' && (
              <div className="md:col-span-2">
                <label className="label">设计音色名（建议填写）</label>
                <input
                  className="input"
                  value={voiceName}
                  onChange={(e) => setVoiceName(e.target.value)}
                  placeholder="例如：霜刃女声_v1（设计模式只使用这个标识）"
                />
                <label className="mt-2 inline-flex items-center gap-2 text-xs text-amber-900">
                  <input
                    type="checkbox"
                    checked={commitToTemp}
                    onChange={(e) => setCommitToTemp(e.target.checked)}
                  />
                  确认落库到 temp（同时生成 personas 映射和生成模板）
                </label>
              </div>
            )}
          </div>
        </Card>

        <Card title="任务信息" subtitle="标题、集数、语气控制">
          <div className="grid gap-3 md:grid-cols-2">
            <div>
              <label className="label">标题</label>
              <input className="input" value={title} onChange={(e) => setTitle(e.target.value)} />
            </div>
            <div>
              <label className="label">集数</label>
              <input className="input" value={episode} onChange={(e) => setEpisode(e.target.value)} />
            </div>
            <div className="md:col-span-2">
              <label className="label">语气描述</label>
              <input className="input" value={tone} onChange={(e) => setTone(e.target.value)} placeholder="例如：低沉、缓慢、压抑" />
            </div>
            <div className="md:col-span-2">
              <label className="label">情绪描述</label>
              <input className="input" value={emotion} onChange={(e) => setEmotion(e.target.value)} placeholder="例如：愤怒、悲悯、阴冷" />
            </div>
            <label className="inline-flex items-center gap-2 text-sm text-amber-900 md:col-span-2">
              <input type="checkbox" checked={emotionPriority} onChange={(e) => setEmotionPriority(e.target.checked)} />
              情绪优先
            </label>
          </div>
        </Card>

        {mode !== 'dialogue' ? (
          <Card title="文案输入" subtitle="单人克隆 / 音色设计">
            {mode === 'design' && (
              <p className="mb-2 text-xs text-amber-900/80">
                设计模式文案可留空（系统自动填默认短句）；若填写则限制 45 字内。
              </p>
            )}
            <textarea
              className="input min-h-40"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder={mode === 'design' ? '可留空；若填写请控制在45字内' : '输入要生成的台词'}
            />
          </Card>
        ) : (
          <Card title="对话编排" subtitle="多角色逐句设置">
            <div className="space-y-4">
              {lines.map((line, idx) => (
                <div key={idx} className="rounded-xl border border-amber-200 bg-amber-50/60 p-3">
                  <div className="grid gap-2 md:grid-cols-2">
                    <select className="input" value={line.role} onChange={(e) => updateLine(idx, 'role', e.target.value)}>
                      <option value="">选择角色</option>
                      {personaOptions.map((opt) => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </select>
                    <input className="input" value={line.tone} onChange={(e) => updateLine(idx, 'tone', e.target.value)} placeholder="语气" />
                  </div>
                  <input className="input mt-2" value={line.emotion} onChange={(e) => updateLine(idx, 'emotion', e.target.value)} placeholder="情绪" />
                  <textarea className="input mt-2 min-h-24" value={line.text} onChange={(e) => updateLine(idx, 'text', e.target.value)} placeholder="台词" />
                  <div className="mt-2 flex items-center justify-between">
                    <label className="inline-flex items-center gap-2 text-xs text-amber-900">
                      <input
                        type="checkbox"
                        checked={line.emotion_priority}
                        onChange={(e) => updateLine(idx, 'emotion_priority', e.target.checked)}
                      />
                      本句情绪优先
                    </label>
                    <Button className="bg-amber-900 hover:bg-black" onClick={() => removeLine(idx)} disabled={lines.length === 1}>删行</Button>
                  </div>
                </div>
              ))}
              <Button onClick={addLine}>新增台词行</Button>
            </div>
          </Card>
        )}

        <Card title="执行区" subtitle="提交任务并查看结果" className="lg:col-span-2">
          <div className="flex flex-wrap items-center gap-3">
            <Button onClick={onGenerate} disabled={loading || uploading}>{loading ? '生成中...' : '开始生成'}</Button>
            {result?.download_url && (
              <a className="rounded-xl border border-amber-700 px-4 py-2 text-sm font-semibold text-amber-900 hover:bg-amber-100" href={result.download_url}>
                下载音频
              </a>
            )}
          </div>
          {message && <p className="mt-3 text-sm text-amber-900">{message}</p>}
          {result?.audio_url && (
            <audio className="mt-4 w-full" controls src={result.audio_url} />
          )}
        </Card>
      </div>
    </div>
  )
}
