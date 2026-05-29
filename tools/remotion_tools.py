"""
Remotion Video Render Tools
Python orqali Remotion (Node.js) video render qilish
"""

import os
import json
import subprocess
import shutil
from pathlib import Path

WORKSPACE = os.getenv("WORKSPACE_DIR", "./workspace")
REMOTION_DIR = os.path.join(os.path.dirname(__file__), "../remotion_project")


def _node_available() -> bool:
    return shutil.which("node") is not None


def _npm_available() -> bool:
    return shutil.which("npm") is not None


def setup_remotion_project() -> dict:
    """Remotion loyihasini bir marta sozlaydi"""
    if not _node_available():
        return {
            "success": False,
            "error": "Node.js o'rnatilmagan!",
            "fix": "https://nodejs.org dan yuklab o'rnating"
        }
    try:
        os.makedirs(REMOTION_DIR, exist_ok=True)
        pkg = os.path.join(REMOTION_DIR, "package.json")
        if not os.path.exists(pkg):
            pkg_data = {
                "name": "jarvis-remotion",
                "version": "1.0.0",
                "scripts": {
                    "build": "remotion render",
                    "studio": "remotion studio"
                },
                "dependencies": {
                    "remotion": "^4.0.0",
                    "@remotion/cli": "^4.0.0",
                    "react": "^18.0.0",
                    "react-dom": "^18.0.0"
                }
            }
            with open(pkg, "w") as f:
                json.dump(pkg_data, f, indent=2)

        # index.tsx
        index_tsx = os.path.join(REMOTION_DIR, "src", "index.tsx")
        os.makedirs(os.path.dirname(index_tsx), exist_ok=True)
        if not os.path.exists(index_tsx):
            with open(index_tsx, "w") as f:
                f.write("""import {registerRoot} from 'remotion';
import {RemotionRoot} from './Root';
registerRoot(RemotionRoot);
""")

        # Root.tsx
        root_tsx = os.path.join(REMOTION_DIR, "src", "Root.tsx")
        if not os.path.exists(root_tsx):
            with open(root_tsx, "w") as f:
                f.write("""import {Composition} from 'remotion';
import {TextVideo} from './TextVideo';
export const RemotionRoot = () => (
  <>
    <Composition id="TextVideo" component={TextVideo}
      durationInFrames={150} fps={30} width={1920} height={1080}
      defaultProps={{text: 'Salom Dunyo!', bgColor: '#0a0a0f', textColor: '#4f8ef7'}}
    />
  </>
);
""")

        # TextVideo.tsx
        comp_tsx = os.path.join(REMOTION_DIR, "src", "TextVideo.tsx")
        if not os.path.exists(comp_tsx):
            with open(comp_tsx, "w") as f:
                f.write("""import {AbsoluteFill, useCurrentFrame, interpolate} from 'remotion';
type Props = {text: string; bgColor: string; textColor: string};
export const TextVideo: React.FC<Props> = ({text, bgColor, textColor}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 30], [0, 1], {extrapolateRight: 'clamp'});
  const scale = interpolate(frame, [0, 30], [0.8, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{background: bgColor, display:'flex', alignItems:'center', justifyContent:'center'}}>
      <div style={{color: textColor, fontSize: 80, fontWeight: 'bold',
        fontFamily: 'sans-serif', opacity, transform: `scale(${scale})`,
        textAlign: 'center', padding: 60}}>{text}</div>
    </AbsoluteFill>
  );
};
""")

        # npm install
        result = subprocess.run(
            ["npm", "install", "--silent"],
            cwd=REMOTION_DIR, capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            return {"success": False, "error": result.stderr[:500]}

        return {"success": True, "message": "✅ Remotion loyihasi sozlandi!", "path": REMOTION_DIR}
    except Exception as e:
        return {"success": False, "error": str(e)}


def render_text_video(
    text: str,
    output_filename: str = "video.mp4",
    bg_color: str = "#0a0a0f",
    text_color: str = "#4f8ef7",
    duration_seconds: int = 5,
    fps: int = 30
) -> dict:
    """Matn bilan oddiy video render qiladi"""
    if not _node_available():
        return {"success": False, "error": "Node.js o'rnatilmagan. https://nodejs.org"}

    try:
        setup = setup_remotion_project()
        if not setup["success"]:
            return setup

        output_path = os.path.join(os.path.abspath(WORKSPACE), output_filename)
        os.makedirs(WORKSPACE, exist_ok=True)

        props = json.dumps({"text": text, "bgColor": bg_color, "textColor": text_color})
        cmd = [
            "npx", "remotion", "render",
            "src/index.tsx", "TextVideo",
            output_path,
            f"--props={props}",
            f"--frames=0-{duration_seconds * fps - 1}",
            f"--fps={fps}",
        ]
        result = subprocess.run(
            cmd, cwd=REMOTION_DIR,
            capture_output=True, text=True, timeout=300
        )
        if result.returncode == 0:
            size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            return {
                "success": True,
                "message": f"✅ Video render qilindi: {output_filename}",
                "path": output_path,
                "size": f"{size // 1024} KB",
                "duration": f"{duration_seconds} soniya",
                "fps": fps
            }
        return {"success": False, "error": result.stderr[-500:]}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Render 5 daqiqada tugamadi"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def render_slideshow(
    slides: list,
    output_filename: str = "slideshow.mp4",
    slide_duration: int = 3
) -> dict:
    """
    Bir necha slayddan iborat video yaratadi
    slides: [{"text": "...", "color": "#fff"}, ...]
    """
    if not _node_available():
        return {"success": False, "error": "Node.js o'rnatilmagan"}
    if not slides:
        return {"success": False, "error": "Kamida 1 ta slayd kerak"}

    try:
        # Har bir slaydni alohida render qilib keyinroq birlashtirish mumkin
        # Hozircha birinchi slaydni render qilamiz
        first = slides[0]
        return render_text_video(
            text=first.get("text", "Slayd"),
            output_filename=output_filename,
            bg_color=first.get("bg_color", "#0a0a0f"),
            text_color=first.get("text_color", "#4f8ef7"),
            duration_seconds=slide_duration * len(slides)
        )
    except Exception as e:
        return {"success": False, "error": str(e)}


def open_remotion_studio() -> dict:
    """Remotion Studio ni brauzerda ochadi"""
    if not _node_available():
        return {"success": False, "error": "Node.js o'rnatilmagan"}
    try:
        setup = setup_remotion_project()
        if not setup["success"]:
            return setup
        subprocess.Popen(
            ["npx", "remotion", "studio", "src/index.tsx"],
            cwd=REMOTION_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return {
            "success": True,
            "message": "✅ Remotion Studio ishga tushdi! Brauzerda: http://localhost:3000"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_rendered_videos() -> dict:
    """Workspace da render qilingan videolar ro'yxati"""
    try:
        videos = []
        for f in Path(WORKSPACE).iterdir():
            if f.suffix in (".mp4", ".webm", ".mov", ".gif"):
                videos.append({
                    "name": f.name,
                    "size": f"{f.stat().st_size // 1024} KB",
                    "path": str(f)
                })
        return {
            "success": True,
            "count": len(videos),
            "videos": videos,
            "message": f"Jami {len(videos)} ta video topildi"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
