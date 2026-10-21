
const modelSelect = document.querySelector('#model');
const fields = document.querySelector('#fields');
const desc = document.querySelector('#modelDesc');
const form = document.querySelector('#predictionForm');
const result = document.querySelector('#result');

const definitions = {
  diabetes: {
    desc: 'Uses age, BMI, glucose and HbA1c plus lifestyle factors.',
    fields: [
      ['gender', 'Gender', 'select', ['Female', 'Male', 'Other']],
      ['age', 'Age (years)', 'number', null, 45],
      ['hypertension', 'Hypertension', 'select', ['0 — No', '1 — Yes'], 0],
      ['heart_disease', 'Heart disease history', 'select', ['0 — No', '1 — Yes'], 0],
      ['smoking_history', 'Smoking history', 'select', ['never', 'No Info', 'former', 'current', 'not current', 'ever']],
      ['bmi', 'BMI', 'number', null, 25],
      ['HbA1c_level', 'HbA1c level', 'number', null, 5.7],
      ['blood_glucose_level', 'Blood glucose level', 'number', null, 110]
    ]
  },

  heart_disease: {
    desc: 'Clinical indicators from the UCI heart dataset. Values use dataset categories.',
    fields: [
      ['age', 'Age', 'number', null, 50],
      ['sex', 'Sex', 'select', ['Female', 'Male']],
      ['cp', 'Chest pain type', 'select', ['typical angina', 'atypical angina', 'non-anginal', 'asymptomatic']],
      ['trestbps', 'Resting blood pressure', 'number', null, 120],
      ['chol', 'Cholesterol', 'number', null, 200],
      ['fbs', 'Fasting blood sugar >120', 'select', ['0 — No', '1 — Yes'], 0],
      ['restecg', 'Resting ECG', 'select', ['normal', 'st-t abnormality', 'lv hypertrophy']],
      ['thalch', 'Maximum heart rate', 'number', null, 150],
      ['exang', 'Exercise angina', 'select', ['0 — No', '1 — Yes'], 0],
      ['oldpeak', 'ST depression', 'number', null, 0],
      ['slope', 'ST slope', 'select', ['upsloping', 'flat', 'downsloping']],
      ['ca', 'Number of major vessels (0–3)', 'number', null, 0],
      ['thal', 'Thalassemia category', 'select', ['normal', 'fixed defect', 'reversable defect']]
    ]
  },

  brfss_diabetes: {
    desc: 'Population-survey factors; categorical codes follow the source dataset.',
    fields: [
      ['Age', 'Age group code', 'number', null, 8],
      ['Sex', 'Sex code', 'select', ['0', '1']],
      ['HighChol', 'High cholesterol', 'select', ['0', '1']],
      ['CholCheck', 'Cholesterol checked', 'select', ['0', '1']],
      ['BMI', 'BMI', 'number', null, 25],
      ['Smoker', 'Smoker', 'select', ['0', '1']],
      ['HeartDiseaseorAttack', 'Heart disease/attack', 'select', ['0', '1']],
      ['PhysActivity', 'Physical activity', 'select', ['0', '1']],
      ['Fruits', 'Eat fruit daily-ish', 'select', ['0', '1']],
      ['Veggies', 'Eat vegetables daily-ish', 'select', ['0', '1']],
      ['HvyAlcoholConsump', 'Heavy alcohol consumption', 'select', ['0', '1']],
      ['GenHlth', 'General health (1–5)', 'number', null, 3],
      ['MentHlth', 'Mental health days (0–30)', 'number', null, 0],
      ['PhysHlth', 'Physical health days (0–30)', 'number', null, 0],
      ['DiffWalk', 'Difficulty walking', 'select', ['0', '1']],
      ['Stroke', 'History of stroke', 'select', ['0', '1']],
      ['HighBP', 'High blood pressure', 'select', ['0', '1']]
    ]
  },

  stroke: {
    desc: 'Demographic and health indicators from a public stroke dataset.',
    fields: [
      ['sex', 'Sex code', 'select', ['0', '1', '2']],
      ['age', 'Age', 'number', null, 45],
      ['hypertension', 'Hypertension', 'select', ['0', '1']],
      ['heart_disease', 'Heart disease', 'select', ['0', '1']],
      ['ever_married', 'Ever married', 'select', ['No', 'Yes']],
      ['work_type', 'Work type code', 'select', ['0', '1', '2', '3', '4']],
      ['Residence_type', 'Residence type code', 'select', ['0', '1']],
      ['avg_glucose_level', 'Average glucose level', 'number', null, 100],
      ['bmi', 'BMI', 'number', null, 25],
      ['smoking_status', 'Smoking status code', 'select', ['0', '1', '2', '3']]
    ]
  },

  kidney: {
    desc: 'Lab values and symptom fields. Leave unknown fields blank; model imputes missing values.',
    fields: [
      ['age', 'Age', 'number', null, 45],
      ['bp', 'Blood pressure', 'number', null, 80],
      ['sg', 'Specific gravity', 'number', null, 1.02],
      ['al', 'Albumin (0–5)', 'number', null, 0],
      ['su', 'Sugar (0–5)', 'number', null, 0],
      ['rbc', 'Red blood cells', 'select', ['normal', 'abnormal']],
      ['pc', 'Pus cell', 'select', ['normal', 'abnormal']],
      ['pcc', 'Pus cell clumps', 'select', ['present', 'notpresent']],
      ['ba', 'Bacteria', 'select', ['present', 'notpresent']],
      ['bgr', 'Blood glucose random', 'number', null, 120],
      ['bu', 'Blood urea', 'number', null, 35],
      ['sc', 'Serum creatinine', 'number', null, 1.2],
      ['sod', 'Sodium', 'number', null, 140],
      ['pot', 'Potassium', 'number', null, 4.5],
      ['hemo', 'Hemoglobin', 'number', null, 13],
      ['pcv', 'Packed cell volume', 'number', null, 40],
      ['wc', 'White blood cell count', 'number', null, 8000],
      ['rc', 'Red blood cell count', 'number', null, 4.5],
      ['htn', 'Hypertension', 'select', ['no', 'yes']],
      ['dm', 'Diabetes mellitus', 'select', ['no', 'yes']],
      ['cad', 'Coronary artery disease', 'select', ['no', 'yes']],
      ['appet', 'Appetite', 'select', ['good', 'poor']],
      ['pe', 'Pedal edema', 'select', ['no', 'yes']],
      ['ane', 'Anemia', 'select', ['no', 'yes']]
    ]
  },

  liver: {
    desc: 'Demographic, lifestyle and liver-function indicators.',
    fields: [
      ['Age', 'Age', 'number', null, 45],
      ['Gender', 'Gender code (dataset)', 'select', ['0', '1']],
      ['BMI', 'BMI', 'number', null, 25],
      ['AlcoholConsumption', 'Alcohol consumption (dataset units)', 'number', null, 2],
      ['Smoking', 'Smoking code', 'select', ['0', '1']],
      ['GeneticRisk', 'Genetic risk code', 'select', ['0', '1', '2']],
      ['PhysicalActivity', 'Physical activity (dataset scale)', 'number', null, 1],
      ['Diabetes', 'Diabetes', 'select', ['0', '1']],
      ['Hypertension', 'Hypertension', 'select', ['0', '1']],
      ['LiverFunctionTest', 'Liver function test value', 'number', null, 40]
    ]
  },

  hypertension: {
    desc: 'Second heart-related dataset; category codes are source-specific.',
    fields: [
      ['age', 'Age', 'number', null, 50],
      ['sex', 'Sex code', 'select', ['0', '1']],
      ['cp', 'Chest pain type code', 'number', null, 2],
      ['trestbps', 'Resting blood pressure', 'number', null, 120],
      ['chol', 'Cholesterol', 'number', null, 200],
      ['fbs', 'Fasting blood sugar flag', 'select', ['0', '1']],
      ['restecg', 'Resting ECG code', 'number', null, 0],
      ['thalach', 'Maximum heart rate', 'number', null, 150],
      ['exang', 'Exercise angina', 'select', ['0', '1']],
      ['oldpeak', 'ST depression', 'number', null, 0],
      ['slope', 'Slope code', 'number', null, 1],
      ['ca', 'Major vessels (0–3)', 'number', null, 0],
      ['thal', 'Thal code', 'number', null, 2]
    ]
  }
};

function makeField(f) {
  const [key, label, type, opts, def] = f;

  const wrap = document.createElement('div');
  wrap.className = 'field';

  const lab = document.createElement('label');
  lab.htmlFor = 'f_' + key;
  lab.textContent = label;
  wrap.appendChild(lab);

  let el;

  if (type === 'select') {
    el = document.createElement('select');

    (opts || []).forEach(opt => {
      const o = document.createElement('option');
      o.value = opt.includes(' — ') ? opt.split(' — ')[0] : opt;
      o.textContent = opt;
      el.appendChild(o);
    });

    if (def !== undefined) {
      el.value = String(def);
    }
  } else {
    el = document.createElement('input');
    el.type = type;
    el.step = 'any';
    el.placeholder = def === undefined ? 'Leave blank if unknown' : String(def);

    if (def !== undefined) {
      el.value = def;
    }
  }

  el.id = 'f_' + key;
  el.dataset.key = key;
  wrap.appendChild(el);

  return wrap;
}

function renderFields() {
  const d = definitions[modelSelect.value];

  if (!d) {
    desc.textContent = 'Choose a prediction model.';
    fields.innerHTML = '';
    return;
  }

  desc.textContent = d.desc;
  fields.innerHTML = '';
  d.fields.forEach(f => fields.appendChild(makeField(f)));
  result.classList.add('hidden');
}

modelSelect.addEventListener('change', renderFields);
renderFields();

function esc(v) {
  return String(v ?? '').replace(/[&<>"']/g, c => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  })[c]);
}

// Health-risk prediction
form.addEventListener('submit', async e => {
  e.preventDefault();

  const features = {};

  fields.querySelectorAll('input, select').forEach(el => {
    const v = el.value;

    if (v === '') {
      features[el.dataset.key] = null;
    } else if (el.tagName === 'SELECT') {
      const raw = v;

      features[el.dataset.key] = [
        'gender', 'smoking_history', 'cp', 'restecg', 'slope',
        'thal', 'rbc', 'pc', 'pcc', 'ba', 'htn', 'dm', 'cad',
        'appet', 'pe', 'ane', 'ever_married'
      ].includes(el.dataset.key)
        ? raw
        : (Number.isFinite(Number(raw)) ? Number(raw) : raw);
    } else {
      features[el.dataset.key] = Number(v);
    }
  });

  const btn = form.querySelector('button');
  btn.disabled = true;
  btn.textContent = 'Analyzing…';

  result.classList.remove('hidden');
  result.innerHTML = '<p>Assessing the provided health information…</p>';

  try {
    const r = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: modelSelect.value,
        features,
        patient_id: document.querySelector('#patientForPrediction').value || null
      })
    });

    const data = await r.json();

    if (!r.ok) {
      throw new Error(data.detail || 'Request failed');
    }

    result.innerHTML = `
      <h3>${esc(data.label || 'Health risk assessment')}</h3>
      <div class="big">${esc(data.result || 'Assessment unavailable')}</div>
      <p>
        This is a model-based screening result, not a confirmed diagnosis.
        It cannot establish whether you have a disease.
        Please consult a qualified healthcare professional to interpret
        the result alongside your symptoms and medical history.
      </p>
      ${
        data.saved_to_patient_history
          ? '<p><b>Assessment saved to the selected patient history.</b></p>'
          : ''
      }
    `;
  } catch (err) {
    result.innerHTML = `
      <h3>Could not complete the assessment</h3>
      <p>${esc(err.message || 'An unexpected error occurred.')}</p>
      <p>Check that the server is running and the required models are available.</p>
    `;
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Run model <span>→</span>';
  }
});

// BMI calculator
document.querySelector('#bmiForm').addEventListener('submit', async e => {
  e.preventDefault();

  const height_cm = Number(document.querySelector('#height').value);
  const weight_kg = Number(document.querySelector('#weight').value);
  const out = document.querySelector('#bmiResult');

  try {
    const r = await fetch('/api/bmi', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ height_cm, weight_kg })
    });

    const d = await r.json();

    if (!r.ok) {
      throw new Error(d.detail || 'Could not calculate BMI');
    }

    out.classList.remove('hidden');
    out.innerHTML = `
      <strong>${esc(d.bmi)}</strong>
      <p>${esc(d.category)}</p>
      <p>${esc(d.note)}</p>
    `;
  } catch (err) {
    out.classList.remove('hidden');
    out.textContent = err.message;
  }
});

// Patient profiles, persistent visit history, CSV upload, and trend comparison.
const patientSelect = document.querySelector('#patientSelect');
const patientForPrediction = document.querySelector('#patientForPrediction');
const patientForm = document.querySelector('#patientForm');

async function apiJson(url, options = {}) {
  const r = await fetch(url, options);
  let d = {};

  try {
    d = await r.json();
  } catch {}

  if (!r.ok) {
    throw new Error(d.detail || 'Request failed');
  }

  return d;
}

function showBox(id, html) {
  const el = document.querySelector('#' + id);
  el.classList.remove('hidden');
  el.innerHTML = html;
}

async function refreshPatients(selectId = '') {
  try {
    const d = await apiJson('/api/patients');

    const options = d.patients.map(p =>
      `<option value="${esc(p.id)}">${esc(p.name)} · ${esc(p.id)} (${p.record_count} records)</option>`
    ).join('');

    patientSelect.innerHTML = '<option value="">Choose a patient</option>' + options;

    patientForPrediction.innerHTML =
      '<option value="">Do not save to a patient</option>' +
      d.patients.map(p =>
        `<option value="${esc(p.id)}">${esc(p.name)} · ${esc(p.id)}</option>`
      ).join('');

    if (selectId) {
      patientSelect.value = selectId;
      patientForPrediction.value = selectId;
    }
  } catch (e) {
    console.error(e);
  }
}

patientForm.addEventListener('submit', async e => {
  e.preventDefault();

  const body = {
    name: document.querySelector('#patientName').value.trim(),
    birth_year: document.querySelector('#birthYear').value
      ? Number(document.querySelector('#birthYear').value)
      : null,
    sex: document.querySelector('#patientSex').value || null,
    consent: document.querySelector('#patientConsent').checked
  };

  try {
    const d = await apiJson('/api/patients', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    showBox(
      'patientCreateResult',
      `<h3>Patient created</h3><p><b>Patient ID:</b> <code>${esc(d.id)}</code></p><p>Save this ID for demo use.</p>`
    );

    await refreshPatients(d.id);
  } catch (err) {
    showBox('patientCreateResult', `<p>${esc(err.message)}</p>`);
  }
});

document.querySelector('#refreshPatients').addEventListener('click', () => {
  refreshPatients();
});

document.querySelector('#loadHistory').addEventListener('click', async () => {
  const id = patientSelect.value;

  if (!id) {
    showBox('patientSummary', '<p>Select a patient first.</p>');
    return;
  }

  try {
    const d = await apiJson('/api/patients/' + encodeURIComponent(id));

    const records = d.records.map(r =>
      `<div class="history-item">
        <b>${esc(r.record_type)}</b> · ${esc(r.recorded_at)}
        <pre>${esc(JSON.stringify(r.measurements, null, 2))}</pre>
        ${r.note ? `<small>${esc(r.note)}</small>` : ''}
      </div>`
    ).join('');

    const uploads = d.uploads.map(u =>
      `<p>📄 ${esc(u.original_name)} · ${u.rows_count} rows · ${esc(u.uploaded_at)}</p>`
    ).join('');

    showBox(
      'patientSummary',
      `<h3>${esc(d.name)} <small>(${esc(d.id)})</small></h3>
       <p>Records: ${d.records.length} · CSV uploads: ${d.uploads.length}</p>
       ${records || '<p>No visits saved yet.</p>'}${uploads}`
    );

    patientForPrediction.value = id;
  } catch (err) {
    showBox('patientSummary', `<p>${esc(err.message)}</p>`);
  }
});

document.querySelector('#recordForm').addEventListener('submit', async e => {
  e.preventDefault();

  const id = patientSelect.value;

  if (!id) {
    showBox('recordResult', '<p>Select a patient first.</p>');
    return;
  }

  const measurements = { _entry_method: 'manual_self_report' };

  const manualFields = [
    ['readingWeight', 'weight_kg'],
    ['readingHeight', 'height_cm'],
    ['readingSystolic', 'systolic_bp_mmhg'],
    ['readingDiastolic', 'diastolic_bp_mmhg'],
    ['readingPulse', 'pulse_bpm'],
    ['readingTemp', 'temperature_c'],
    ['readingGlucose', 'glucose_mg_dl']
  ];

  let entered = 0;

  for (const [field, key] of manualFields) {
    const raw = document.querySelector('#' + field).value;

    if (raw !== '') {
      measurements[key] = Number(raw);
      entered++;
    }
  }

  if (measurements.height_cm && measurements.weight_kg) {
    measurements.bmi = Number(
      (measurements.weight_kg / ((measurements.height_cm / 100) ** 2)).toFixed(1)
    );
  }

  let extra = {};
  const extraRaw = document.querySelector('#measurements').value.trim();

  if (extraRaw) {
    try {
      extra = JSON.parse(extraRaw);

      if (!extra || Array.isArray(extra) || typeof extra !== 'object') {
        throw new Error();
      }
    } catch {
      showBox('recordResult', '<p>Advanced measurements must be a valid JSON object.</p>');
      return;
    }

    for (const [k, v] of Object.entries(extra)) {
      if (k === '_entry_method' || (typeof v === 'object' && v !== null)) {
        showBox(
          'recordResult',
          '<p>Advanced measurements must use simple values and cannot override the entry-method marker.</p>'
        );
        return;
      }

      measurements[k] = v;
      entered++;
    }
  }

  if (entered === 0) {
    showBox(
      'recordResult',
      '<p>Enter at least one reading before saving. Leave unknown readings blank; do not guess.</p>'
    );
    return;
  }

  const dateValue = document.querySelector('#recordedAt').value;
  const noteText = document.querySelector('#recordNote').value.trim();

  const note = [
    noteText,
    'Entry method: manually entered by user; values are not independently verified.'
  ].filter(Boolean).join(' | ');

  const body = {
    record_type: document.querySelector('#recordType').value,
    measurements,
    note,
    recorded_at: dateValue ? new Date(dateValue).toISOString() : null
  };

  try {
    const d = await apiJson(
      `/api/patients/${encodeURIComponent(id)}/records`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      }
    );

    showBox(
      'recordResult',
      `<p>${esc(d.message)} Record #${d.id}</p>
       <p>Saved ${entered} entered reading(s).
       ${measurements.bmi ? `BMI calculated from the height and weight you entered: ${measurements.bmi}.` : ''}
       This records information only; it does not guarantee a valid ML prediction.</p>`
    );

    e.target.reset();
    await refreshPatients(id);
  } catch (err) {
    showBox('recordResult', `<p>${esc(err.message)}</p>`);
  }
});

document.querySelector('#uploadForm').addEventListener('submit', async e => {
  e.preventDefault();

  const id = patientSelect.value;
  const file = document.querySelector('#csvFile').files[0];

  if (!id) {
    showBox('uploadResult', '<p>Select a patient first.</p>');
    return;
  }

  if (!file) return;

  const fd = new FormData();
  fd.append('file', file);

  try {
    const d = await apiJson(
      `/api/patients/${encodeURIComponent(id)}/upload-csv`,
      { method: 'POST', body: fd }
    );

    showBox(
      'uploadResult',
      `<p>${esc(d.message)}</p><p>${d.rows} rows · columns: ${esc(d.columns.join(', '))}</p>`
    );

    await refreshPatients(id);
  } catch (err) {
    showBox('uploadResult', `<p>${esc(err.message)}</p>`);
  }
});

document.querySelector('#reportForm').addEventListener('submit', async e => {
  e.preventDefault();

  const id = patientSelect.value;
  const file = document.querySelector('#reportFile').files[0];

  if (!id) {
    showBox('reportResult', '<p>Select a patient first. Create a profile if needed.</p>');
    return;
  }

  if (!file) return;

  const fd = new FormData();
  fd.append('file', file);

  showBox('reportResult', '<p>Reading PDF text…</p>');

  try {
    const d = await apiJson(
      `/api/patients/${encodeURIComponent(id)}/upload-report`,
      { method: 'POST', body: fd }
    );

    const vals = Object.entries(d.extracted_values || {})
      .map(([k, v]) =>
        `<li><b>${esc(v.display_name)}</b>: ${esc(v.value)} ${esc(v.unit)} <small>key: ${esc(k)}</small></li>`
      ).join('');

    showBox(
      'reportResult',
      `<h3>${esc(d.message)}</h3>
       <p>${d.pages} pages · ${d.extracted_count} possible readings · saved to history: ${d.saved_to_history ? 'yes' : 'no'}</p>
       ${vals
         ? `<p><b>Possible extracted readings (verify each one):</b></p><ul>${vals}</ul>`
         : '<p>No readable numeric lab values were detected. If this is a scanned/image PDF, manual entry may be needed; OCR is not included.</p>'}
       <p class="privacy-note">${esc(d.warning)}</p>
       <p>Use Compare a measurement with the exact key shown to compare numeric readings over time.</p>`
    );

    await refreshPatients(id);
  } catch (err) {
    showBox('reportResult', `<p>${esc(err.message)}</p>`);
  }
});

document.querySelector('#compareButton').addEventListener('click', async () => {
  const id = patientSelect.value;
  const metric = document.querySelector('#compareMetric').value.trim();

  if (!id || !metric) {
    showBox('comparisonResult', '<p>Select a patient and enter a measurement key.</p>');
    return;
  }

  try {
    const d = await apiJson(
      `/api/patients/${encodeURIComponent(id)}/comparison?metric=${encodeURIComponent(metric)}`
    );

    const pts = d.points.map(p =>
      `<li>${esc(p.recorded_at)}: <b>${esc(p.value)}</b> (${esc(p.record_type)})</li>`
    ).join('');

    const change = d.change_from_previous === null
      ? 'Need at least two numeric records to calculate change.'
      : `Change from previous record: <b>${d.change_from_previous > 0 ? '+' : ''}${d.change_from_previous}</b>`;

    showBox(
      'comparisonResult',
      `${pts ? `<ul>${pts}</ul>` : '<p>No numeric values found for this exact key.</p>'}
       <p>${change}</p><small>${esc(d.note)}</small>`
    );
  } catch (err) {
    showBox('comparisonResult', `<p>${esc(err.message)}</p>`);
  }
});

refreshPatients();
