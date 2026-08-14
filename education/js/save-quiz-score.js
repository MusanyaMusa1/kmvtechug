/**
 * KMVTECH Education - Save Graded Quiz Score
 * 
 * Add this to every MODULE GRADED QUIZ page (not practice quizzes).
 * Call saveQuizScore() after the student submits and the score is calculated.
 * 
 * HOW TO USE:
 * 1. Upload this file to: education/js/save-quiz-score.js
 * 2. Add to every graded quiz page <head> (after supabase):
 *    <script src="/education/js/save-quiz-score.js"></script>
 * 3. In your submitQuiz() function, after calculating score, add:
 *    await saveQuizScore('EVL1', 1, score, total);
 *    (replace EVL1 with course code, 1 with module number)
 * 
 * The function saves every attempt but the grades page shows best score only.
 */

async function saveQuizScore(courseCode, moduleNumber, score, total) {
  try {
    const SB = supabase.createClient(
      'https://nzjojrebyvxuawnkitth.supabase.co',
      'sb_publishable_EKcJxtkPvorUeuLB9Q2xLA_SYIWzDDa'
    );

    const { data: { session } } = await SB.auth.getSession();
    if (!session) return;

    const percentage = Math.round((score / total) * 100);
    const passed = percentage >= 70;

    await SB.from('quiz_attempts').insert({
      student_id: session.user.id,
      course_code: courseCode,
      module_number: moduleNumber,
      score: score,
      total: total,
      percentage: percentage,
      passed: passed
    });

  } catch (err) {
    // Silent fail - never break the quiz for a save error
    console.log('Score save:', err.message);
  }
}
