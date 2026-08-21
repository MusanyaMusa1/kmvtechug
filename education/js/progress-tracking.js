/**
 * KMVTECH Education - Progress Tracking
 * Official master file - managed by platform team only
 * Place at: education/js/progress-tracking.js
 */

const COURSE_TOTALS = {
  // Law
  'EVL1':     56,
  'EVL2':     133,
  'EQT1':     94,
  // Social Sciences / Psychology
  'ENVPSY':   78,
  'COGPSY':   64,
  'SOCPSY':   62,
  // Business
  'HRM1':     101,
  // IT and Digital Skills
  'DIGSK':    62,
  'INTRAI':   62,
  'AIPROMPT': 62,
  'CYBERSEC': 62,
  'ETHHACK':  62,
  'HCI':      62,
  // Health Sciences
  'FAEC':     62,
  'COMH':     62,
  'IPC1':     62,
  'MNCH':     62,
  'NCDPC':    62,
  'FAMMED':   62,
  'REPURO':   62,
  'FOUNDHP':  62,
  'MHWP':     62,
  'HCPE':     62,
  'INTEPI':   62,
  'NUTHW':    62,
  'MEETH':    62,
};

async function trackProgress() {
  try {
    const SB = supabase.createClient(
      'https://nzjojrebyvxuawnkitth.supabase.co',
      'sb_publishable_EKcJxtkPvorUeuLB9Q2xLA_SYIWzDDa'
    );
    const { data: { session } } = await SB.auth.getSession();
    if (!session) return;
    const courseCode = document.body.dataset.course;
    if (!courseCode) return;
    let pagePath = window.location.pathname;
    if (!pagePath.endsWith('/')) pagePath += '/';
    await SB.from('lesson_progress').upsert({
      student_id: session.user.id,
      course_code: courseCode,
      page_path: pagePath
    }, { onConflict: 'student_id,course_code,page_path' });
    await updatePageProgressBar(SB, session.user.id, courseCode);
  } catch (err) {
    console.log('Progress tracking:', err.message);
  }
}

async function updatePageProgressBar(SB, studentId, courseCode) {
  try {
    const total = COURSE_TOTALS[courseCode];
    if (!total) return;
    const { count } = await SB
      .from('lesson_progress')
      .select('id', { count: 'exact', head: true })
      .eq('student_id', studentId)
      .eq('course_code', courseCode);
    const pct = Math.min(Math.round((count / total) * 100), 100);
    const fill = document.querySelector('.pfill');
    if (fill) fill.style.width = pct + '%';
  } catch (err) {
    console.log('Progress bar:', err.message);
  }
}

async function getAllProgress(SB, studentId, courseCodes) {
  const result = {};
  for (const code of courseCodes) {
    try {
      const total = COURSE_TOTALS[code] || 1;
      const { count } = await SB
        .from('lesson_progress')
        .select('id', { count: 'exact', head: true })
        .eq('student_id', studentId)
        .eq('course_code', code);
      const { data: last } = await SB
        .from('lesson_progress')
        .select('page_path, completed_at')
        .eq('student_id', studentId)
        .eq('course_code', code)
        .order('completed_at', { ascending: false })
        .limit(1)
        .maybeSingle();
      result[code] = {
        percent: Math.min(Math.round(((count || 0) / total) * 100), 100),
        completed: count || 0,
        total: total,
        lastPage: last ? last.page_path : null
      };
    } catch (err) {
      result[code] = { percent: 0, completed: 0, total: COURSE_TOTALS[code] || 1, lastPage: null };
    }
  }
  return result;
}
