/**
 * KMVTECH Education - Progress Tracking
 * 
 * HOW TO USE ON EVERY LESSON/QUIZ PAGE:
 * 
 * 1. Add this script tag to the page (after supabase.js):
 *    <script src="/education/js/progress-tracking.js"></script>
 * 
 * 2. Call trackProgress() inside your show() function, AFTER content is shown:
 *    function show() {
 *      document.getElementById('lk').style.display = 'none';
 *      const lc = document.getElementById('lc');
 *      if (lc) lc.style.display = 'block';
 *      trackProgress(); // <-- ADD THIS LINE
 *    }
 * 
 * 3. Set the course code on the <body> tag:
 *    <body data-course="EVL1">
 * 
 * That is all. The rest is automatic.
 */

// Total pages per course - update as courses are added
const COURSE_TOTALS = {
  'EVL1': 56,  // 40 lesson pages + 8 practice quizzes + 8 graded quizzes
  // Add others as courses are built:
  // 'FAM1': 0,
  // 'CRM1': 0,
};

async function trackProgress() {
  try {
    const SB = supabase.createClient(
      'https://nzjojrebyvxuawnkitth.supabase.co',
      'sb_publishable_EKcJxtkPvorUeuLB9Q2xLA_SYIWzDDa'
    );

    // Get current session
    const { data: { session } } = await SB.auth.getSession();
    if (!session) return;

    // Get course code from body tag
    const courseCode = document.body.dataset.course;
    if (!courseCode) return;

    // Get current page path (normalize trailing slash)
    let pagePath = window.location.pathname;
    if (!pagePath.endsWith('/')) pagePath += '/';

    // Record this page as visited (UPSERT - safe to call multiple times)
    await SB.from('lesson_progress').upsert({
      student_id: session.user.id,
      course_code: courseCode,
      page_path: pagePath
    }, { onConflict: 'student_id,course_code,page_path' });

    // Update progress bar on current page if it exists
    await updatePageProgressBar(SB, session.user.id, courseCode);

  } catch (err) {
    // Silent fail - never break the lesson for a tracking error
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

    // Update the sticky progress bar fill
    const fill = document.querySelector('.pfill');
    if (fill) fill.style.width = pct + '%';

  } catch (err) {
    console.log('Progress bar update:', err.message);
  }
}

/**
 * GET PROGRESS FOR DASHBOARD
 * Call this from the dashboard to get progress for all courses a student is enrolled in.
 * Returns: { courseCode: { percent, completed, total, lastPage } }
 */
async function getAllProgress(SB, studentId, courseCodes) {
  const result = {};
  for (const code of courseCodes) {
    try {
      const total = COURSE_TOTALS[code] || 1;

      // Get count of completed pages
      const { count } = await SB
        .from('lesson_progress')
        .select('id', { count: 'exact', head: true })
        .eq('student_id', studentId)
        .eq('course_code', code);

      // Get last visited page for resume
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
