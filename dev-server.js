/**
 * SmartLearn - All-in-One Local Development Server (Node.js)
 * Full dynamic mock endpoints supporting:
 * - GET /health
 * - POST /api/auth/login
 * - POST /api/auth/register
 * - GET /api/courses (with subject & level filters)
 * - POST /api/courses (teacher create course)
 * - GET /api/courses/:id/materials
 * - GET /api/quizzes/:id
 * - POST /api/quizzes/:id/submit (instant scoring & feedback)
 * - GET /api/me/results (student quiz history)
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT_DIR = __dirname;
const FRONTEND_DIR = path.join(ROOT_DIR, 'frontend');

// In-memory dynamic database for courses, materials, quizzes, and results
let courses = [
  {
    id: 1,
    title: "Advanced Mathematics",
    subject: "Mathematics",
    level: "S6",
    teacher: "Mr. Habimana",
    teacher_name: "Mr. Habimana",
    teacher_id: 1,
    notesCount: 24,
    description: "Calculus, vectors in 3D, trigonometry, and national past exam papers with step-by-step solutions.",
    image: "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?auto=format&fit=crop&w=600&q=80",
    materials: [
      { id: 101, title: "Differential Calculus Summary", type: "PDF", size: "180 KB", link: "#" },
      { id: 102, title: "3D Vectors & Matrices Cheat Sheet", type: "PDF", size: "210 KB", link: "#" },
      { id: 103, title: "National Exam 2024 Solved Paper", type: "PDF", size: "350 KB", link: "#" }
    ]
  },
  {
    id: 2,
    title: "Modern Physics",
    subject: "Physics",
    level: "S6",
    teacher: "Dr. Uwase",
    teacher_name: "Dr. Uwase",
    teacher_id: 2,
    notesCount: 18,
    description: "Classical mechanics, wave optics, electromagnetic induction, and experimental problem sets.",
    image: "https://images.unsplash.com/photo-1636466497217-26a8cbeaf0aa?auto=format&fit=crop&w=600&q=80",
    materials: [
      { id: 201, title: "Electromagnetism Formulas & Laws", type: "PDF", size: "145 KB", link: "#" },
      { id: 202, title: "Quantum & Atomic Physics Review", type: "PDF", size: "190 KB", link: "#" }
    ]
  },
  {
    id: 3,
    title: "Organic & Physical Chemistry",
    subject: "Chemistry",
    level: "S5",
    teacher: "Mrs. Mukamana",
    notesCount: 15,
    description: "Hydrocarbons, reaction mechanisms, stoichiometry, redox titration, and chemical kinetics.",
    image: "https://images.unsplash.com/photo-1603126857599-f6e157fa2fe6?auto=format&fit=crop&w=600&q=80",
    materials: [
      { id: 301, title: "Organic Functional Groups Chart", type: "PDF", size: "120 KB", link: "#" },
      { id: 302, title: "Reaction Mechanisms Walkthrough", type: "PDF", size: "230 KB", link: "#" }
    ]
  },
  {
    id: 4,
    title: "General & Cellular Biology",
    subject: "Biology",
    level: "S4",
    teacher: "Mr. Karemera",
    notesCount: 20,
    description: "Mendelian genetics, cellular respiration, human organ physiology, and lightweight illustrated diagrams.",
    image: "https://images.unsplash.com/photo-1530026405186-ed1f139313f8?auto=format&fit=crop&w=600&q=80",
    materials: [
      { id: 401, title: "Cell Structure & Organelles Summary", type: "PDF", size: "95 KB", link: "#" },
      { id: 402, title: "Genetics & Punnett Squares Guide", type: "PDF", size: "160 KB", link: "#" }
    ]
  }
];

let quizzes = {
  1: {
    id: 1,
    courseId: 1,
    title: "Senior 6 Mathematics Quiz: Derivatives & Vectors",
    questions: [
      {
        id: 1,
        question: "What is the derivative of f(x) = 3x² + 4x - 5?",
        options: ["6x + 4", "3x + 4", "6x² + 4", "6x - 5"],
        correctIndex: 0,
        explanation: "Applying the power rule d/dx(ax^n) = n*a*x^(n-1): 3*(2x) + 4 = 6x + 4."
      },
      {
        id: 2,
        question: "What is the dot product of vectors u = (2, 3) and v = (4, -1)?",
        options: ["5", "11", "8", "-5"],
        correctIndex: 0,
        explanation: "u · v = (2 * 4) + (3 * -1) = 8 - 3 = 5."
      },
      {
        id: 3,
        question: "Evaluate the integral ∫ 2x dx:",
        options: ["x² + C", "2x² + C", "x + C", "2 + C"],
        correctIndex: 0,
        explanation: "The antiderivative of 2x is 2*(x²/2) + C = x² + C."
      }
    ]
  },
  2: {
    id: 2,
    courseId: 2,
    title: "Senior 6 Physics Quiz: Mechanics & Electromagnetism",
    questions: [
      {
        id: 1,
        question: "Which law states that induced EMF is proportional to the rate of change of magnetic flux?",
        options: ["Faraday's Law", "Ohm's Law", "Coulomb's Law", "Newton's First Law"],
        correctIndex: 0,
        explanation: "Faraday's Law of Induction states EMF = -dΦ/dt."
      },
      {
        id: 2,
        question: "What is the SI unit of electric capacitance?",
        options: ["Farad (F)", "Henry (H)", "Tesla (T)", "Weber (Wb)"],
        correctIndex: 0,
        explanation: "Capacitance is measured in Farads (F)."
      }
    ]
  }
};

let userResults = [
  {
    id: 1,
    quizTitle: "Mathematics S6: Calculus Basics",
    score: 3,
    total: 3,
    percentage: 100,
    date: "2026-11-06",
    status: "Passed"
  },
  {
    id: 2,
    quizTitle: "Physics S6: Wave Mechanics",
    score: 2,
    total: 2,
    percentage: 100,
    date: "2026-11-05",
    status: "Passed"
  }
];

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

function readBody(req) {
  return new Promise((resolve) => {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        resolve(JSON.parse(body || '{}'));
      } catch {
        resolve({});
      }
    });
  });
}

async function handleRequest(req, res) {
  // CORS Headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  const parsedUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const pathname = parsedUrl.pathname;

  // 1. Health check
  if (pathname === '/health' || pathname === '/api/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'ok',
      app: 'SmartLearn API',
      environment: 'development'
    }));
    return;
  }

  // Browser navigation shortcuts & Friendly Redirects
  if (req.method === 'GET') {
    if (pathname === '/auth/login' || pathname === '/api/auth/login' || pathname === '/login' || pathname === '/login.html') {
      const accept = req.headers['accept'] || '';
      if (accept.includes('application/json')) {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          endpoint: '/auth/login',
          method: 'POST',
          description: 'Authenticate with email and password to receive a JWT access token.',
          required_body: { email: 'student@smartlearn.rw', password: 'Password123!' }
        }));
        return;
      }
      res.writeHead(302, { 'Location': '/frontend/pages/login.html' });
      res.end();
      return;
    }

    if (pathname === '/auth/register' || pathname === '/api/auth/register' || pathname === '/register' || pathname === '/register.html') {
      const accept = req.headers['accept'] || '';
      if (accept.includes('application/json')) {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          endpoint: '/auth/register',
          method: 'POST',
          description: 'Register a new user account.',
          required_body: { full_name: 'Jane Doe', email: 'jane@smartlearn.rw', password: 'Password123!', role: 'student' }
        }));
        return;
      }
      res.writeHead(302, { 'Location': '/frontend/pages/register.html' });
      res.end();
      return;
    }

    if (pathname === '/dashboard' || pathname === '/dashboard.html') {
      res.writeHead(302, { 'Location': '/frontend/pages/dashboard.html' });
      res.end();
      return;
    }
  }

  // 2. Auth Endpoints
  if ((pathname === '/auth/login' || pathname === '/api/auth/login') && req.method === 'POST') {
    const payload = await readBody(req);
    const username = payload.email ? payload.email.split('@')[0] : (payload.username || 'student');
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      access_token: 'jwt_' + Buffer.from(username + ':' + Date.now()).toString('base64'),
      token_type: 'bearer',
      user: {
        username: username,
        name: payload.full_name || username.charAt(0).toUpperCase() + username.slice(1),
        email: username.includes('@') ? username : `${username.toLowerCase()}@smartlearn.rw`,
        role: payload.role || 'student'
      }
    }));
    return;
  }

  if ((pathname === '/auth/register' || pathname === '/api/auth/register') && req.method === 'POST') {
    res.writeHead(201, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', message: 'User registered successfully' }));
    return;
  }

  if ((pathname === '/auth/me' || pathname === '/api/auth/me') && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      id: 1,
      username: 'student',
      full_name: 'Student User',
      name: 'Student User',
      email: 'student@smartlearn.rw',
      role: 'student'
    }));
    return;
  }

  // 3. Courses API
  if ((pathname === '/courses' || pathname === '/api/courses') && req.method === 'GET') {
    const subject = parsedUrl.searchParams.get('subject');
    const level = parsedUrl.searchParams.get('level');
    const teacherId = parsedUrl.searchParams.get('teacher_id');
    let filtered = courses;
    if (subject && subject !== 'all') {
      filtered = filtered.filter(c => c.subject.toLowerCase() === subject.toLowerCase());
    }
    if (level && level !== 'all') {
      filtered = filtered.filter(c => c.level.toLowerCase() === level.toLowerCase());
    }
    if (teacherId) {
      filtered = filtered.filter(c => String(c.teacher_id) === String(teacherId));
    }
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(filtered));
    return;
  }

  if ((pathname === '/courses' || pathname === '/api/courses') && req.method === 'POST') {
    const newCourse = await readBody(req);
    newCourse.id = courses.length + 1;
    newCourse.teacher_id = newCourse.teacher_id || 1;
    newCourse.teacher_name = newCourse.teacher_name || newCourse.teacher || "Mr. Habimana";
    newCourse.notesCount = 0;
    newCourse.materials = [];
    newCourse.image = "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=600&q=80";
    courses.push(newCourse);
    res.writeHead(201, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(newCourse));
    return;
  }

  // PATCH /courses/:id
  if ((pathname.startsWith('/courses/') || pathname.startsWith('/api/courses/')) && req.method === 'PATCH') {
    const parts = pathname.split('/');
    const courseId = parseInt(parts[parts.length - 1], 10);
    const body = await readBody(req);
    const course = courses.find(c => c.id === courseId);
    if (!course) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ detail: 'Course not found' }));
      return;
    }
    Object.assign(course, body);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(course));
    return;
  }

  // DELETE /courses/:id
  if ((pathname.startsWith('/courses/') || pathname.startsWith('/api/courses/')) && req.method === 'DELETE') {
    const parts = pathname.split('/');
    const courseId = parseInt(parts[parts.length - 1], 10);
    const index = courses.findIndex(c => c.id === courseId);
    if (index === -1) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ detail: 'Course not found' }));
      return;
    }
    courses.splice(index, 1);
    res.writeHead(204);
    res.end();
    return;
  }

    // 3.5 Course Materials & Quizzes API
  if ((pathname.includes('/courses/') && pathname.endsWith('/materials')) && req.method === 'GET') {
    const parts = pathname.split('/');
    const cIdx = parts.indexOf('courses');
    const courseId = parseInt(parts[cIdx + 1], 10);
    const course = courses.find(c => c.id === courseId) || courses[0];
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(course.materials || []));
    return;
  }

  if ((pathname.includes('/courses/') && pathname.endsWith('/materials')) && req.method === 'POST') {
    const parts = pathname.split('/');
    const cIdx = parts.indexOf('courses');
    const courseId = parseInt(parts[cIdx + 1], 10);
    const body = await readBody(req);
    const course = courses.find(c => c.id === courseId);
    if (!course) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ detail: 'Course not found' }));
      return;
    }
    course.materials = course.materials || [];
    const newMaterial = {
      id: course.materials.length + 101,
      course_id: courseId,
      title: body.title || 'Course Notes',
      content: body.content || body.notes || '',
      link_url: body.link_url || body.link || '#',
      type: 'PDF',
      size: '140 KB'
    };
    course.materials.push(newMaterial);
    course.notesCount = course.materials.length;
    res.writeHead(201, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(newMaterial));
    return;
  }

  if ((pathname.includes('/courses/') && pathname.endsWith('/quizzes')) && req.method === 'GET') {
    const parts = pathname.split('/');
    const cIdx = parts.indexOf('courses');
    const courseId = parseInt(parts[cIdx + 1], 10);
    const courseQuizzes = Object.values(quizzes).filter(q => q.courseId === courseId);
    const result = courseQuizzes.length > 0 ? courseQuizzes : [
      { id: 1, courseId: courseId, title: "Curriculum Diagnostic Quiz", questions: [ { id: 1 } ] }
    ];
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(result.map(q => ({
      id: q.id,
      title: q.title,
      course_id: q.courseId,
      question_count: q.questions ? q.questions.length : 3
    }))));
    return;
  }

  if ((pathname.includes('/courses/') && pathname.endsWith('/quizzes')) && req.method === 'POST') {
    const parts = pathname.split('/');
    const cIdx = parts.indexOf('courses');
    const courseId = parseInt(parts[cIdx + 1], 10);
    const body = await readBody(req);
    const newQuizId = Object.keys(quizzes).length + 1;
    const formattedQuestions = (body.questions || []).map((q, idx) => {
      const opts = (q.options || []).map((opt, oIdx) => ({
        id: oIdx + 1,
        text: typeof opt === 'object' ? opt.text : opt,
        is_correct: typeof opt === 'object' ? !!opt.is_correct : false
      }));
      const correctIdx = opts.findIndex(o => o.is_correct);
      return {
        id: idx + 1,
        question: q.text || q.question,
        text: q.text || q.question,
        options: opts,
        correctIndex: correctIdx >= 0 ? correctIdx : 0,
        explanation: q.explanation || "National exam syllabus review."
      };
    });
    quizzes[newQuizId] = {
      id: newQuizId,
      courseId: courseId,
      title: body.title || `Quiz ${newQuizId}`,
      description: body.description || '',
      questions: formattedQuestions
    };
    res.writeHead(201, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      id: newQuizId,
      course_id: courseId,
      title: quizzes[newQuizId].title,
      description: quizzes[newQuizId].description,
      questions: formattedQuestions
    }));
    return;
  }

  // 4. Quizzes API
  if (pathname.includes('/quizzes/') && pathname.endsWith('/submit') && req.method === 'POST') {
    const parts = pathname.split('/');
    const qIdx = parts.indexOf('quizzes');
    const quizId = parseInt(parts[qIdx + 1], 10) || 1;
    const body = await readBody(req);
    const answers = body.answers || {};
    const quiz = quizzes[quizId] || quizzes[1];

    let score = 0;
    const feedback = [];

    // Support list [ { question_id, option_id } ] or object answers
    (quiz.questions || []).forEach((q, idx) => {
      let selected = -1;
      if (Array.isArray(answers)) {
        const found = answers.find(a => a.question_id === q.id || a.question_id === (idx + 1));
        if (found) selected = found.option_id;
      } else if (answers[idx] !== undefined) {
        selected = parseInt(answers[idx], 10);
      }
      const isCorrect = selected === q.correctIndex || selected === (q.correctIndex + 1);
      if (isCorrect) score++;

      feedback.push({
        question_id: q.id,
        question_text: q.question || q.text,
        selected_option_id: selected,
        correct_option_id: q.correctIndex,
        is_correct: isCorrect,
        explanation: q.explanation || "National exam syllabus review."
      });
    });

    const totalQuestions = quiz.questions ? quiz.questions.length : 1;
    const percentage = Math.round((score / totalQuestions) * 100);
    const attempt = {
      attempt_id: userResults.length + 1,
      id: userResults.length + 1,
      quiz_id: quizId,
      quiz_title: quiz.title,
      quizTitle: quiz.title,
      score,
      total: totalQuestions,
      percentage,
      submitted_at: new Date().toISOString(),
      date: new Date().toISOString().split('T')[0],
      status: percentage >= 60 ? 'Passed' : 'Needs Review'
    };
    userResults.unshift(attempt);

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      score,
      total: totalQuestions,
      percentage,
      feedback,
      attempt
    }));
    return;
  }

  // Teacher Quiz Results API (Issue 19)
  if (pathname.includes('/quizzes/') && pathname.endsWith('/results') && req.method === 'GET') {
    const parts = pathname.split('/');
    const qIdx = parts.indexOf('quizzes');
    const quizId = parseInt(parts[qIdx + 1], 10) || 1;
    const attempts = userResults.filter(r => r.quiz_id === quizId);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(attempts.length > 0 ? attempts : userResults.slice(0, 3)));
    return;
  }

  // Single Quiz GET (Issue 16)
  if ((pathname.startsWith('/quizzes/') || pathname.startsWith('/api/quizzes/')) && !pathname.endsWith('/submit') && !pathname.endsWith('/results') && !pathname.endsWith('/answer-key') && req.method === 'GET') {
    const parts = pathname.split('/');
    const qIdx = parts.indexOf('quizzes');
    const quizId = parseInt(parts[qIdx + 1], 10) || 1;
    const quiz = quizzes[quizId] || quizzes[1];
    const studentQuiz = {
      id: quiz.id,
      title: quiz.title,
      description: quiz.description,
      questions: (quiz.questions || []).map(q => ({
        id: q.id,
        text: q.question || q.text,
        question: q.question || q.text,
        options: (q.options || []).map((opt, oIdx) => ({
          id: typeof opt === 'object' ? (opt.id || oIdx + 1) : (oIdx + 1),
          text: typeof opt === 'object' ? opt.text : opt
        }))
      }))
    };
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(studentQuiz));
    return;
  }

  // 5. Results History API
  if ((pathname === '/me/results' || pathname === '/api/me/results') && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(userResults));
    return;
  }

  // 6. Static files serving
  let relativePath = pathname === '/' ? '/frontend/index.html' : pathname;
  if (relativePath.startsWith('/pages/') || relativePath.startsWith('/css/') || relativePath.startsWith('/js/') || relativePath.startsWith('/assets/')) {
    relativePath = '/frontend' + relativePath;
  }

  let filePath = path.join(ROOT_DIR, relativePath);

  if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
    filePath = path.join(filePath, 'index.html');
  }

  if (!fs.existsSync(filePath)) {
    const altPath = path.join(FRONTEND_DIR, pathname);
    if (fs.existsSync(altPath) && !fs.statSync(altPath).isDirectory()) {
      filePath = altPath;
    }
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(`<h3>404 Not Found</h3><p>File not found: <code>${pathname}</code></p><p><a href="/frontend/index.html">Back to SmartLearn</a></p>`);
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  });
}

// Start listeners on Port 8000 and 5500
const server8000 = http.createServer(handleRequest);
server8000.listen(8000, () => {
  console.log('SmartLearn Dev Server running at: http://localhost:8000');
});

const server5500 = http.createServer(handleRequest);
server5500.listen(5500, () => {
  console.log('SmartLearn Dev Server running at: http://localhost:5500');
});
