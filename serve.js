const express = require('express');
const path = require('path');
const app = express();
const PORT = 3000;

// Serve static files from front/dist
app.use(express.static(path.join(__dirname, 'front/dist')));

// Serve TIF files
app.use('/data/tif', express.static(path.join(__dirname, 'data/tif')));
app.use('/data/masks', express.static(path.join(__dirname, 'data/masks')));

// Serve all other requests to index.html (for SPA routing)
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'front/dist/index.html'));
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
