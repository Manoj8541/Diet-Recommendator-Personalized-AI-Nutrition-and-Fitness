import { useState, useMemo, useEffect } from 'react'
import './App.css'

const NUTRITION_FACTS = [
  '⚡ Protein has the highest thermic effect (TEF) — burning up to 25-30% of its calories just during digestion!',
  '💧 Drinking 500ml of water can temporarily boost your resting metabolic rate by 24-30% within 10 minutes.',
  '🥗 Consuming dietary fiber slows gastric emptying and stabilizes blood glucose, reducing hunger cravings.',
  '🏋️ Resistance training during a caloric deficit signals your body to burn stored fat while preserving lean muscle mass.',
  '🥑 Healthy fats (monounsaturated & omega-3s) are essential for hormone production and nutrient absorption.',
  '🌙 Quality sleep of 7-8 hours regulates ghrelin and leptin — your body’s primary hunger and satiety hormones.'
]

function App() {
  // Fresh, blank initial state as requested
  const [formData, setFormData] = useState({
    age: '',
    weight_kg: '',
    height_cm: '',
    sex: 'male',
    diet_type: 'veg',
    activity_level: 'moderate',
    goal: 'lose',
    allergies: '',
    free_text: ''
  })

  const [loading, setLoading] = useState(false)
  const [loadingFactIndex, setLoadingFactIndex] = useState(0)
  const [loadingProgress, setLoadingProgress] = useState(20)
  const [result, setResult] = useState(null)
  const [rejectionMessage, setRejectionMessage] = useState(null)
  const [networkError, setNetworkError] = useState(null)
  const [activeTab, setActiveTab] = useState('weekday')
  const [copySuccess, setCopySuccess] = useState(false)

  // Rotate fun facts and progress bar during generation (engaging timepass for user)
  useEffect(() => {
    let factInterval
    let progressInterval
    if (loading) {
      setLoadingProgress(25)
      factInterval = setInterval(() => {
        setLoadingFactIndex((prev) => (prev + 1) % NUTRITION_FACTS.length)
      }, 1800)

      progressInterval = setInterval(() => {
        setLoadingProgress((prev) => {
          if (prev >= 92) return prev
          return prev + Math.floor(Math.random() * 15 + 8)
        })
      }, 350)
    } else {
      setLoadingProgress(100)
    }
    return () => {
      clearInterval(factInterval)
      clearInterval(progressInterval)
    }
  }, [loading])

  // Real-time live metabolic calculation preview (medically accurate Mifflin-St Jeor)
  const liveMetrics = useMemo(() => {
    const age = parseInt(formData.age, 10)
    const weight = parseFloat(formData.weight_kg)
    const height = parseFloat(formData.height_cm)

    if (!age || !weight || !height || age <= 0 || weight <= 0 || height <= 0) {
      return null
    }

    const heightM = height / 100
    const bmi = +(weight / (heightM * heightM)).toFixed(1)
    let bmiCategory = 'Normal Weight'
    if (bmi < 18.5) bmiCategory = 'Underweight'
    else if (bmi >= 25 && bmi < 30) bmiCategory = 'Overweight'
    else if (bmi >= 30) bmiCategory = 'Obese'

    // Gender-specific Mifflin-St Jeor calculation
    const bmr = formData.sex === 'male'
      ? Math.round(10 * weight + 6.25 * height - 5 * age + 5)
      : Math.round(10 * weight + 6.25 * height - 5 * age - 161)

    const mult = formData.activity_level === 'active' ? 1.725 : formData.activity_level === 'moderate' ? 1.55 : 1.2
    const tdee = Math.round(bmr * mult)

    let calorieTarget = tdee
    if (formData.goal === 'lose') calorieTarget = Math.max(1100, tdee - 500)
    else if (formData.goal === 'gain') calorieTarget = tdee + 500

    let proMult = 1.4
    if (formData.goal === 'lose') proMult = 2.0
    else if (formData.goal === 'gain') proMult = formData.activity_level === 'active' ? 2.2 : 2.0
    else if (age >= 50) proMult = 1.6
    const proteinTarget = Math.round(weight * proMult)

    const baseWater = weight * 35 + (formData.activity_level === 'active' ? 750 : formData.activity_level === 'moderate' ? 500 : 250)
    const waterLiters = +(baseWater / 1000).toFixed(1)

    return {
      bmi,
      bmiCategory,
      bmr,
      tdee,
      calorieTarget,
      proteinTarget,
      waterLiters
    }
  }, [formData.age, formData.weight_kg, formData.height_cm, formData.sex, formData.activity_level, formData.goal])

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const toggleAllergyTag = (tag) => {
    const current = formData.allergies ? formData.allergies.split(',').map(s => s.trim()).filter(Boolean) : []
    const index = current.indexOf(tag)
    if (index > -1) {
      current.splice(index, 1)
    } else {
      current.push(tag)
    }
    setFormData({
      ...formData,
      allergies: current.join(', ')
    })
  }

  const handleReset = () => {
    setFormData({
      age: '',
      weight_kg: '',
      height_cm: '',
      sex: 'male',
      diet_type: 'veg',
      activity_level: 'moderate',
      goal: 'lose',
      allergies: '',
      free_text: ''
    })
    setResult(null)
    setRejectionMessage(null)
    setNetworkError(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setNetworkError(null)
    setRejectionMessage(null)

    // Guardrail pre-check on client
    const offTopicKeywords = ['order', 'burger', 'pizza', 'weather', 'poem', 'joke', 'movie', 'code', 'python', 'uber', 'zomato', 'swiggy']
    const freeTextLower = (formData.free_text || '').toLowerCase()
    const isOffTopic = offTopicKeywords.some(k => freeTextLower.includes(k))

    if (formData.free_text && isOffTopic) {
      setRejectionMessage("I can only assist with diet-related queries.")
      setResult(null)
      return
    }

    setLoading(true)

    try {
      const response = await fetch('http://localhost:8000/generate-diet', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          age: parseInt(formData.age, 10),
          weight_kg: parseFloat(formData.weight_kg),
          height_cm: parseFloat(formData.height_cm),
          sex: formData.sex,
          diet_type: formData.diet_type,
          activity_level: formData.activity_level,
          goal: formData.goal,
          allergies: formData.allergies.trim() || null,
          free_text: formData.free_text.trim() || null
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Server error (${response.status})`)
      }

      const data = await response.json()

      if (data.message && !data.calorie_target && !data.user_metrics) {
        setRejectionMessage(data.message)
        setResult(null)
      } else {
        setResult(data)
        setActiveTab('weekday')
        setTimeout(() => {
          document.getElementById('plan-results')?.scrollIntoView({ behavior: 'smooth' })
        }, 100)
      }
    } catch (err) {
      setNetworkError(err.message || 'Unable to connect to the backend server. Please ensure FastAPI is running.')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = () => {
    if (!result) return
    const metrics = result.user_metrics || liveMetrics || {}
    const text = `
# 🥗 Personalized Diet & Workout Plan
- Daily Calories: ${result.calorie_target || metrics.calorie_target || metrics.calorieTarget} kcal
- Target Protein: ${metrics.protein_target_g || metrics.proteinTarget}g | Water: ${metrics.water_intake_liters || metrics.waterLiters}L
- BMI: ${metrics.bmi} (${metrics.bmi_category || metrics.bmiCategory}) | BMR: ${metrics.bmr} kcal | TDEE: ${metrics.tdee} kcal

## 📅 Weekday Plan
- 🌅 Breakfast: ${result.weekday_plan?.breakfast?.name} (${result.weekday_plan?.breakfast?.calories || ''} kcal, ${result.weekday_plan?.breakfast?.protein_g || ''}g protein)
- 🌞 Lunch: ${result.weekday_plan?.lunch?.name} (${result.weekday_plan?.lunch?.calories || ''} kcal, ${result.weekday_plan?.lunch?.protein_g || ''}g protein)
- 🌙 Dinner: ${result.weekday_plan?.dinner?.name} (${result.weekday_plan?.dinner?.calories || ''} kcal, ${result.weekday_plan?.dinner?.protein_g || ''}g protein)
- 🍎 Snacks: ${result.weekday_plan?.snacks?.name} (${result.weekday_plan?.snacks?.calories || ''} kcal, ${result.weekday_plan?.snacks?.protein_g || ''}g protein)

## 🎉 Weekend Plan
- 🌅 Breakfast: ${result.weekend_plan?.breakfast?.name}
- 🌞 Lunch: ${result.weekend_plan?.lunch?.name}
- 🌙 Dinner: ${result.weekend_plan?.dinner?.name}
- 🍎 Snacks: ${result.weekend_plan?.snacks?.name}

## 🏋️ Workout Routine
- Type: ${result.exercise_plan?.workout_type || 'Custom Routine'} (${result.exercise_plan?.weekly_frequency || ''})
- Recovery: ${result.exercise_plan?.recovery_tips || ''}

## 💡 Clinical Tips
${result.notes}
`.trim()

    navigator.clipboard.writeText(text)
    setCopySuccess(true)
    setTimeout(() => setCopySuccess(false), 2500)
  }

  const renderMealCard = (icon, title, themeClass, mealData) => {
    if (!mealData) return null
    const isObject = typeof mealData === 'object' && mealData !== null
    const name = isObject ? mealData.name : mealData
    const portion = isObject ? mealData.portion : '1 serving'
    const calories = isObject ? mealData.calories : null
    const protein = isObject ? mealData.protein_g : null
    const nutrients = isObject ? mealData.key_nutrients : null
    const alternative = isObject ? mealData.alternative : null

    return (
      <div className={`meal-card ${themeClass}`}>
        <div className="meal-card-header">
          <span className="meal-badge">
            <span className="meal-emoji">{icon}</span> {title}
          </span>
          {portion && <span className="portion-tag">{portion}</span>}
        </div>

        <div className="meal-card-body">
          <h4 className="meal-dish-title">{name}</h4>

          {(calories || protein) && (
            <div className="macros-row">
              {calories && <span className="macro-chip cal-chip">⚡ {calories} kcal</span>}
              {protein && <span className="macro-chip pro-chip">🥩 {protein}g Protein</span>}
            </div>
          )}

          {nutrients && (
            <div className="nutrient-callout">
              <span className="sparkle">✨</span> {nutrients}
            </div>
          )}

          {alternative && (
            <div className="alt-box">
              <span className="alt-tag">🔄 Option B:</span> {alternative}
            </div>
          )}
        </div>
      </div>
    )
  }

  const commonAllergens = ['Dairy', 'Peanuts', 'Tree Nuts', 'Gluten', 'Eggs', 'Soy', 'Shellfish']

  return (
    <div className="app-shell">
      {/* Background Lighting Gradients */}
      <div className="ambient-blob blob-green"></div>
      <div className="ambient-blob blob-blue"></div>
      <div className="ambient-blob blob-purple"></div>

      {/* Main Top Header */}
      <header className="app-header">
        <div className="header-inner">
          <div className="brand-logo-group">
            <span className="brand-icon">🥗</span>
            <div className="brand-text">
              <h1 className="brand-title">Diet Recommendator</h1>
              <p className="brand-tagline">AI-Powered Nutrition, Macro Targets & Workout Protocol</p>
            </div>
          </div>
          <span className="badge-pill">Clinical Diet Engine</span>
        </div>
      </header>

      {/* Main Split Grid */}
      <div className="main-grid">
        {/* Left Form Card */}
        <section className="form-card-container">
          <div className="glass-panel form-panel">
            <div className="panel-title-bar">
              <h2>📋 Your Information</h2>
              <button type="button" className="reset-btn" onClick={handleReset} title="Clear all fields">
                Reset
              </button>
            </div>

            <form onSubmit={handleSubmit} className="diet-form">
              {/* Row 1: Age, Weight, Height */}
              <div className="form-triad">
                <div className="form-field">
                  <label htmlFor="age">Age</label>
                  <div className="input-affix-wrapper">
                    <input
                      type="number"
                      id="age"
                      name="age"
                      value={formData.age}
                      onChange={handleChange}
                      required
                      min="10"
                      max="100"
                      placeholder="e.g. 25"
                    />
                    <span className="affix-text">yrs</span>
                  </div>
                </div>

                <div className="form-field">
                  <label htmlFor="weight_kg">Weight</label>
                  <div className="input-affix-wrapper">
                    <input
                      type="number"
                      id="weight_kg"
                      name="weight_kg"
                      value={formData.weight_kg}
                      onChange={handleChange}
                      required
                      min="20"
                      max="500"
                      step="0.5"
                      placeholder="e.g. 70"
                    />
                    <span className="affix-text">kg</span>
                  </div>
                </div>

                <div className="form-field">
                  <label htmlFor="height_cm">Height</label>
                  <div className="input-affix-wrapper">
                    <input
                      type="number"
                      id="height_cm"
                      name="height_cm"
                      value={formData.height_cm}
                      onChange={handleChange}
                      required
                      min="50"
                      max="300"
                      step="0.5"
                      placeholder="e.g. 175"
                    />
                    <span className="affix-text">cm</span>
                  </div>
                </div>
              </div>

              {/* Row 2: Gender, Diet Type, Activity */}
              <div className="form-triad">
                <div className="form-field">
                  <label htmlFor="sex">Gender</label>
                  <select id="sex" name="sex" value={formData.sex} onChange={handleChange} required>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </div>

                <div className="form-field">
                  <label htmlFor="diet_type">Dietary Preference</label>
                  <select id="diet_type" name="diet_type" value={formData.diet_type} onChange={handleChange} required>
                    <option value="veg">🥬 Vegetarian</option>
                    <option value="non-veg">🍗 Non-Vegetarian</option>
                  </select>
                </div>

                <div className="form-field">
                  <label htmlFor="activity_level">Physical Activity</label>
                  <select id="activity_level" name="activity_level" value={formData.activity_level} onChange={handleChange} required>
                    <option value="sedentary">🛋️ Sedentary</option>
                    <option value="moderate">🏃 Moderate (3-5d)</option>
                    <option value="active">🏋️ Active (6-7d)</option>
                  </select>
                </div>
              </div>

              {/* Row 3: Goal */}
              <div className="form-field full-width">
                <label htmlFor="goal">Goal</label>
                <select id="goal" name="goal" value={formData.goal} onChange={handleChange} required>
                  <option value="lose">Weight Loss</option>
                  <option value="gain">Weight Gain</option>
                  <option value="maintain">Maintain</option>
                </select>
              </div>

              {/* Row 4: Allergies with quick chips */}
              <div className="form-field full-width">
                <label>Allergies & Food Exclusions (Optional)</label>
                <div className="allergy-chips-container">
                  {commonAllergens.map((tag) => {
                    const active = formData.allergies.toLowerCase().includes(tag.toLowerCase())
                    return (
                      <button
                        type="button"
                        key={tag}
                        className={`allergy-chip ${active ? 'active-chip' : ''}`}
                        onClick={() => toggleAllergyTag(tag)}
                      >
                        {active ? `✓ ${tag}` : `+ ${tag}`}
                      </button>
                    )
                  })}
                </div>
                <input
                  type="text"
                  name="allergies"
                  value={formData.allergies}
                  onChange={handleChange}
                  placeholder="Or type custom restrictions (e.g. peanuts, dairy, gluten)"
                  className="sub-input"
                />
              </div>

              {/* Row 5: Free text preferences */}
              <div className="form-field full-width">
                <label htmlFor="free_text">Custom Diet Preferences (Optional)</label>
                <textarea
                  id="free_text"
                  name="free_text"
                  value={formData.free_text}
                  onChange={handleChange}
                  rows="2"
                  placeholder="e.g. High protein, rich in fiber, quick 15-minute preparation"
                ></textarea>
              </div>

              {/* Submit CTA */}
              <button type="submit" className="submit-cta-btn" disabled={loading}>
                {loading ? '⚡ Crafting Your AI Protocol...' : '🚀 Calculate & Generate Plan'}
              </button>
            </form>

            {/* Interactive Loading Timepass Box */}
            {loading && (
              <div className="loading-card-box">
                <div className="loading-bar-wrapper">
                  <div className="loading-bar-fill" style={{ width: `${loadingProgress}%` }}></div>
                </div>
                <div className="fact-box">
                  <div className="fact-header">💡 Nutrition Fast Fact</div>
                  <p className="fact-content">{NUTRITION_FACTS[loadingFactIndex]}</p>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Right Column: Live Metrics & Protocol Results */}
        <section className="results-card-container" id="plan-results">
          {/* Live Metabolic Cards */}
          <div className="glass-panel live-metrics-strip">
            <div className="metrics-strip-header">
              <h3>⚡ Metabolic Assessment</h3>
              <span className="live-pill">Live Preview</span>
            </div>

            <div className="metrics-cards-row">
              <div className="metric-box calorie-box">
                <div className="m-title">🎯 Calorie Target</div>
                <div className="m-value">{result?.calorie_target || liveMetrics?.calorieTarget || '—'} <span className="m-unit">kcal</span></div>
                <div className="m-subtext">
                  {formData.goal === 'lose' ? '500 kcal deficit' : formData.goal === 'gain' ? '500 kcal surplus' : 'Maintenance'}
                </div>
              </div>

              <div className="metric-box bmi-box">
                <div className="m-title">⚖️ BMI</div>
                <div className="m-value">{result?.user_metrics?.bmi || liveMetrics?.bmi || '—'}</div>
                <div className="m-subtext">
                  {liveMetrics || result?.user_metrics ? (
                    <span className={`status-badge ${(result?.user_metrics?.bmi_category || liveMetrics?.bmiCategory) === 'Normal Weight' ? 'status-good' : 'status-warn'}`}>
                      {result?.user_metrics?.bmi_category || liveMetrics?.bmiCategory}
                    </span>
                  ) : (
                    <span className="status-badge status-good">Enter details</span>
                  )}
                </div>
              </div>

              <div className="metric-box protein-box">
                <div className="m-title">🥩 Target Protein</div>
                <div className="m-value">{result?.user_metrics?.protein_target_g || liveMetrics?.proteinTarget || '—'} <span className="m-unit">g</span></div>
                <div className="m-subtext">Optimal daily target</div>
              </div>

              <div className="metric-box water-box">
                <div className="m-title">💧 Daily Water</div>
                <div className="m-value">{result?.user_metrics?.water_intake_liters || liveMetrics?.waterLiters || '—'} <span className="m-unit">L</span></div>
                <div className="m-subtext">~{Math.round(((result?.user_metrics?.water_intake_liters || liveMetrics?.waterLiters) || 2.5) * 4)} glasses</div>
              </div>

              <div className="metric-box tdee-box">
                <div className="m-title">🔥 BMR / TDEE</div>
                <div className="m-value">{result?.user_metrics?.tdee || liveMetrics?.tdee || '—'} <span className="m-unit">TDEE</span></div>
                <div className="m-subtext">BMR: {result?.user_metrics?.bmr || liveMetrics?.bmr || '—'} kcal</div>
              </div>
            </div>
          </div>

          {/* Guardrail Rejection Alert */}
          {rejectionMessage && (
            <div className="alert-card guardrail-rejection">
              <div className="alert-title">🛡️ Guardrail Rejection Notice</div>
              <div className="alert-body">{rejectionMessage}</div>
              <div className="alert-hint">Please enter a valid nutrition or fitness-related request.</div>
            </div>
          )}

          {/* Network Error Alert */}
          {networkError && (
            <div className="alert-card error-alert">
              <div className="alert-title">⚠️ System Error</div>
              <div className="alert-body">{networkError}</div>
            </div>
          )}

          {/* Result Protocol Card */}
          {result && (
            <div className="glass-panel protocol-panel">
              <div className="protocol-header">
                <div>
                  <h3>🥗 Your Custom Nutrition & Fitness Protocol</h3>
                  <div className="protocol-tags">
                    <span className="ptag">{formData.diet_type === 'veg' ? '🥬 Vegetarian' : '🍗 Non-Vegetarian'}</span>
                    <span className="ptag ptag-goal">{formData.goal === 'lose' ? 'Weight Loss' : formData.goal === 'gain' ? 'Weight Gain' : 'Maintenance'}</span>
                    <span className="ptag ptag-gender">{formData.sex === 'male' ? 'Male' : 'Female'} • Age {formData.age || '25'}</span>
                  </div>
                </div>

                <div className="action-buttons-group">
                  <button type="button" className="action-btn copy-btn" onClick={copyToClipboard}>
                    {copySuccess ? '✅ Copied!' : '📋 Copy Plan'}
                  </button>
                  <button type="button" className="action-btn print-btn" onClick={() => window.print()}>
                    🖨️ Print
                  </button>
                </div>
              </div>

              {/* Navigation Tabs */}
              <div className="tabs-header">
                <button
                  className={`tab-btn ${activeTab === 'weekday' ? 'active-tab' : ''}`}
                  onClick={() => setActiveTab('weekday')}
                >
                  📅 Weekday Meals
                </button>
                <button
                  className={`tab-btn ${activeTab === 'weekend' ? 'active-tab' : ''}`}
                  onClick={() => setActiveTab('weekend')}
                >
                  🎉 Weekend Meals
                </button>
                <button
                  className={`tab-btn ${activeTab === 'exercise' ? 'active-tab' : ''}`}
                  onClick={() => setActiveTab('exercise')}
                >
                  🏋️ Workout Routine
                </button>
                <button
                  className={`tab-btn ${activeTab === 'nutrients' ? 'active-tab' : ''}`}
                  onClick={() => setActiveTab('nutrients')}
                >
                  💊 Key Nutrients
                </button>
              </div>

              {/* Tab Contents */}
              <div className="tab-pane-container">
                {activeTab === 'weekday' && (
                  <div className="meals-grid-layout">
                    {renderMealCard('🌅', 'Breakfast', 'theme-breakfast', result.weekday_plan?.breakfast)}
                    {renderMealCard('🌞', 'Lunch', 'theme-lunch', result.weekday_plan?.lunch)}
                    {renderMealCard('🌙', 'Dinner', 'theme-dinner', result.weekday_plan?.dinner)}
                    {renderMealCard('🍎', 'Snacks', 'theme-snacks', result.weekday_plan?.snacks)}
                  </div>
                )}

                {activeTab === 'weekend' && (
                  <div className="meals-grid-layout">
                    {renderMealCard('🌅', 'Weekend Breakfast', 'theme-breakfast', result.weekend_plan?.breakfast)}
                    {renderMealCard('🌞', 'Weekend Lunch', 'theme-lunch', result.weekend_plan?.lunch)}
                    {renderMealCard('🌙', 'Weekend Dinner', 'theme-dinner', result.weekend_plan?.dinner)}
                    {renderMealCard('🍎', 'Weekend Snacks', 'theme-snacks', result.weekend_plan?.snacks)}
                  </div>
                )}

                {activeTab === 'exercise' && result.exercise_plan && (
                  <div className="exercise-section-view">
                    <div className="routine-banner">
                      <span className="routine-badge">🎯 {result.exercise_plan.weekly_frequency || '4 Sessions / Week'}</span>
                      <h4>{result.exercise_plan.workout_type || 'Prescribed Workout Protocol'}</h4>
                    </div>

                    <div className="exercise-cols-grid">
                      <div className="exercise-col-card">
                        <h5>🏋️ Strength & Resistance Focus</h5>
                        <ul>
                          {(result.exercise_plan.strength_focus || []).map((item, i) => (
                            <li key={i}><span className="bullet-point">✓</span> {item}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="exercise-col-card">
                        <h5>🏃 Cardio & Conditioning</h5>
                        <ul>
                          {(result.exercise_plan.cardio_focus || []).map((item, i) => (
                            <li key={i}><span className="bullet-point">✓</span> {item}</li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {result.exercise_plan.recovery_tips && (
                      <div className="recovery-notes-box">
                        <h6>🧘 Recovery & Sleep Protocol</h6>
                        <p>{result.exercise_plan.recovery_tips}</p>
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'nutrients' && result.key_nutrients && (
                  <div className="nutrients-grid-layout">
                    {result.key_nutrients.map((n, idx) => (
                      <div key={idx} className="nutrient-box">
                        <h4>✨ {n.nutrient}</h4>
                        <p className="n-benefit-text">{n.benefit}</p>
                        {n.recommended_foods && (
                          <div className="n-sources-area">
                            <span className="n-sources-label">Top Food Sources:</span>
                            <div className="n-sources-chips">
                              {n.recommended_foods.map((food, fIdx) => (
                                <span key={fIdx} className="n-source-pill">{food}</span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Notes */}
              {result.notes && (
                <div className="clinical-notes-card">
                  <h5>💡 Clinical Guidelines & Recommendations</h5>
                  <p>{result.notes}</p>
                </div>
              )}
            </div>
          )}

          {/* Empty Placeholder */}
          {!result && !loading && !rejectionMessage && !networkError && (
            <div className="glass-panel empty-banner">
              <div className="empty-emoji">🥗</div>
              <h4>Instant Assessment Ready</h4>
              <p>Enter your age, weight, and height on the left, then click <strong>"Calculate & Generate Plan"</strong> to get your complete diet and fitness plan.</p>
            </div>
          )}
        </section>
      </div>
    </div>
  )
}

export default App
