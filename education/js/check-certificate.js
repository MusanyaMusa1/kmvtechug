/**
 * KMVTECH Education - Auto Certificate Trigger
 * Place at: education/js/check-certificate.js
 * 
 * Add to every MODULE GRADED QUIZ page:
 * <script src="/education/js/check-certificate.js"></script>
 * 
 * Call after saveQuizScore() in sub() function:
 * await saveQuizScore('EVL1', 1, score, total);
 * await checkAndIssueCertificate('EVL1', 8);
 */

const CERT_THRESHOLD = 80;

const COURSE_MODULES_COUNT = {
  'EVL1': 8, 'EVL2': 8, 'ENVPSY': 9,
  'HRM1': 9, 'COGPSY': 6, 'SOCPSY': 6, 'EQT1': 6,
};

async function checkAndIssueCertificate(courseCode, totalModules) {
  try {
    const SB = supabase.createClient(
      'https://nzjojrebyvxuawnkitth.supabase.co',
      'sb_publishable_EKcJxtkPvorUeuLB9Q2xLA_SYIWzDDa'
    );
    const { data: { session } } = await SB.auth.getSession();
    if (!session) return;
    const studentId = session.user.id;
    const modCount = totalModules || COURSE_MODULES_COUNT[courseCode] || 8;

    // Already has certificate?
    const { data: existing } = await SB.from('certificates')
      .select('id').eq('student_id', studentId).eq('course_code', courseCode).maybeSingle();
    if (existing) return;

    // Get all attempts
    const { data: attempts } = await SB.from('quiz_attempts')
      .select('module_number, percentage')
      .eq('student_id', studentId).eq('course_code', courseCode);
    if (!attempts || attempts.length === 0) return;

    // Best per module
    const best = {};
    for (const a of attempts) {
      const m = a.module_number;
      if (!best[m] || a.percentage > best[m]) best[m] = a.percentage;
    }

    // All modules done?
    if (Object.keys(best).length < modCount) return;

    // Average
    const scores = Object.values(best);
    const avg = Math.round(scores.reduce((s, n) => s + n, 0) / scores.length);
    if (avg < CERT_THRESHOLD) return;

    // Get profile and course
    const [{ data: profile }, { data: course }] = await Promise.all([
      SB.from('profiles').select('full_name, student_number').eq('id', studentId).maybeSingle(),
      SB.from('courses').select('title').eq('course_code', courseCode).maybeSingle()
    ]);
    if (!profile) return;

    // Generate verification code
    const year = new Date().getFullYear();
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let rand = '';
    for (let i = 0; i < 6; i++) rand += chars[Math.floor(Math.random() * chars.length)];
    const verificationCode = courseCode + '-' + year + '-' + rand;

    // Insert certificate
    const { error } = await SB.from('certificates').insert({
      student_id: studentId,
      course_code: courseCode,
      course_title: course?.title || courseCode,
      student_name: profile.full_name,
      student_number: profile.student_number,
      overall_score: avg,
      verification_code: verificationCode,
    });

    if (!error) showCertBanner(avg, verificationCode);

  } catch (err) {
    console.log('Certificate check:', err.message);
  }
}

function showCertBanner(avg, code) {
  const el = document.createElement('div');
  el.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:9999;background:linear-gradient(135deg,#0D1B2A,#2B3FBF);color:#fff;padding:20px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.3);';
  el.innerHTML = '<div style="font-size:28px;margin-bottom:8px;">&#127881; &#127891; &#127881;</div>'
    + '<div style="font-family:Playfair Display,serif;font-weight:800;font-size:1.2rem;margin-bottom:4px;">Certificate Earned!</div>'
    + '<div style="font-size:13px;color:rgba(255,255,255,0.8);margin-bottom:12px;">You achieved ' + avg + '% average. Your certificate is now ready.</div>'
    + '<div style="font-family:monospace;font-size:12px;color:#C9922A;margin-bottom:14px;">Code: ' + code + '</div>'
    + '<a href="/education/certificates/" style="display:inline-flex;align-items:center;gap:8px;background:#C9922A;color:#0D1B2A;text-decoration:none;font-weight:700;font-size:13px;padding:10px 20px;border-radius:8px;">View My Certificates &#8594;</a>'
    + '<button onclick="this.parentElement.remove()" style="position:absolute;top:12px;right:16px;background:none;border:none;color:rgba(255,255,255,0.5);font-size:20px;cursor:pointer;">&#215;</button>';
  document.body.appendChild(el);
}
