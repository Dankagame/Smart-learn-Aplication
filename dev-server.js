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

  // 4. Quizzes API
  if (pathname.startsWith('/api/quizzes/') && pathname.endsWith('/submit') && req.method === 'POST') {
    const quizId = parseInt(pathname.split('/')[3], 10);
    const body = await readBody(req);
    const answers = body.answers || {};
    const quiz = quizzes[quizId] || quizzes[1];

    let score = 0;
    const feedback = [];

    quiz.questions.forEach((q, idx) => {
      const selected = answers[idx] !== undefined ? parseInt(answers[idx], 10) : -1;
      const isCorrect = selected === q.correctIndex;
      if (isCorrect) score++;

      feedback.push({
        questionId: q.id,
        question: q.question,
        selectedOption: selected,
        correctOption: q.correctIndex,
        isCorrect,
        explanation: q.explanation
      });
    });

    const percentage = Math.round((score / quiz.questions.length) * 100);
    const attempt = {
      id: userResults.length + 1,
      quizTitle: quiz.title,
      score,
      total: quiz.questions.length,
      percentage,
      date: new Date().toISOString().split('T')[0],
      status: percentage >= 50 ? 'Passed' : 'Needs Review'
    };
    userResults.unshift(attempt);

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      score,
      total: quiz.questions.length,
      percentage,
      feedback,
      attempt
    }));
    return;
  }

  if ((pathname.startsWith('/quizzes/') || pathname.startsWith('/api/quizzes/')) && req.method === 'GET') {
    const quizId = parseInt(pathname.split('/')[3], 10);
    const quiz = quizzes[quizId] || quizzes[1];
    // Strip correct answers when sending to students
    const studentQuiz = {
      id: quiz.id,
      title: quiz.title,
      questions: quiz.questions.map(q => ({
        id: q.id,
        question: q.question,
        options: q.options
      }))
    };
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(studentQuiz));
    return;
  }

  // 5. Results History API
  if (pathname === '/api/me/results' && req.method === 'GET') {
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
