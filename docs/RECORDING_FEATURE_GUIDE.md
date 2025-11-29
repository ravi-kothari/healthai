# Recording Feature Implementation Guide

## Overview

The recording functionality has been integrated directly into the SOAP Notes Editor, providing a streamlined workflow for doctors to record patient visits and generate clinical documentation.

## New Components

### RecordingControls Component

Location: `frontend/components/visit/RecordingControls.tsx`

This component provides a complete recording workflow with multiple states:

#### States

1. **Idle State** (No recording)
   - Shows a prominent red "Record" button
   - Primary action in the SOAP Notes interface

2. **Active Recording State**
   - Shows "Stop" button to end recording
   - Displays running timer (MM:SS format)
   - Shows audio visualizer with pulsing bars
   - Red pulsing indicator confirms recording is active

3. **Post-Recording State** (Recording stopped, not transcribed)
   - "Discard & Re-record" button to start over
   - "Transcribe Recording" button to process audio
   - Shows recording duration

4. **Post-Transcription State** (Transcription available)
   - "Discard" button to remove and start fresh
   - "Generate SOAP Notes" button to create clinical notes
   - Live transcription preview panel showing the transcribed text
   - Green checkmark indicating transcription is ready

## Features

### Audio Recording
- Browser-based audio recording using MediaRecorder API
- Automatic microphone permission request
- WebM audio format for broad compatibility

### Real-time Feedback
- **Recording Timer**: Shows elapsed time during recording
- **Audio Visualizer**: Pulsing bars that respond to audio input
- **Visual Indicators**: Color-coded states (red for recording, green for ready)

### Live Transcription Preview
- After transcription completes, shows preview of transcribed text
- Scrollable preview panel (max 40px height)
- Blue-themed preview box for easy identification

### Workflow Integration
- Seamlessly integrates with existing SOAP Notes generation
- Auto-enables "Generate from Transcription" button when ready
- Maintains state across component interactions

## Updated Components

### SOAPNotesEditor Component

Location: `frontend/components/visit/SOAPNotesEditor.tsx`

**Changes:**
1. Added RecordingControls import
2. Added state for managing current transcription:
   - `currentTranscriptId`: Tracks the active transcription
   - `hasRecording`: Boolean flag to enable/disable SOAP generation
3. Added `handleTranscriptionComplete` callback to receive transcription data
4. Updated `handleGenerateSOAP` to use the current transcript ID
5. Reorganized button layout:
   - RecordingControls as primary action (left side)
   - Secondary actions grouped (right side, auto-align)
   - "Save Notes" button highlighted in green

## User Workflow

### Complete Recording Flow

```
1. Doctor clicks "Record" button
   ↓
2. Browser requests microphone permission (first time only)
   ↓
3. Recording starts
   - Timer begins counting
   - Audio visualizer shows activity
   - Red pulsing indicator confirms recording
   ↓
4. Doctor clicks "Stop" when finished
   ↓
5. Recording stops
   - Options: "Discard & Re-record" or "Transcribe Recording"
   ↓
6. Doctor clicks "Transcribe Recording"
   - Audio uploads to backend
   - Processing indicator shown
   ↓
7. Transcription completes
   - Preview shown in blue panel
   - "Generate SOAP Notes" button becomes active
   ↓
8. Doctor reviews transcription preview
   - Can discard and re-record if needed
   - Or proceed to generate SOAP notes
   ↓
9. Doctor clicks "Generate SOAP Notes"
   - AI processes transcription
   - SOAP sections auto-populate
   ↓
10. Doctor reviews and edits SOAP notes
    - Can refine individual sections with AI
    - Can insert templates
    ↓
11. Doctor clicks "Save Notes"
    - Notes saved to patient visit record
```

## Technical Details

### Audio Processing

```typescript
// Recording setup
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const mediaRecorder = new MediaRecorder(stream);

// Audio visualization
const audioContext = new AudioContext();
const analyser = audioContext.createAnalyser();
analyser.fftSize = 256;
```

### State Management

The component manages multiple pieces of state:

```typescript
const [isRecording, setIsRecording] = useState(false);
const [recordingTime, setRecordingTime] = useState(0);
const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
const [liveTranscript, setLiveTranscript] = useState('');
const [isProcessing, setIsProcessing] = useState(false);
const [transcriptionId, setTranscriptionId] = useState<string | null>(null);
```

### API Integration

```typescript
// Upload and transcribe
const response = await apiClient.uploadAudioTranscription(visitId, audioFile);
const transcription = response.data;

// Generate SOAP notes
const response = await apiClient.generateSOAPNotes(visitId, transcriptionId);
```

## Design Decisions

### UX Considerations

1. **Prominent Placement**: Record button is the first action in the SOAP Notes interface
   - Establishes clear workflow: Record → Generate → Save
   - Follows natural left-to-right progression

2. **Visual Hierarchy**:
   - Red "Record" button draws attention as primary action
   - Green "Save Notes" button stands out as final action
   - Outline buttons for secondary actions (templates, etc.)

3. **Progressive Disclosure**:
   - UI adapts to current state
   - Only shows relevant actions at each step
   - Reduces cognitive load

4. **Continuous Feedback**:
   - Timer confirms recording is active
   - Visualizer shows audio is being captured
   - Transcription preview builds confidence in accuracy

### Accessibility

- Clear button labels (not icon-only)
- Color-coded states (red/green) with text labels
- Keyboard accessible (all button controls)
- Visual feedback for all state changes

### Error Handling

- Browser permission errors → User-friendly toast notification
- Upload failures → Retry option available
- No need to re-record if transcription fails

## Browser Compatibility

The recording feature requires:
- MediaDevices API support
- MediaRecorder API support
- AudioContext API support

Supported browsers:
- Chrome/Edge 49+
- Firefox 25+
- Safari 14.1+

## Future Enhancements

Potential improvements:
1. Real-time transcription during recording (streaming)
2. Speaker diarization (identify patient vs. doctor)
3. Audio quality indicators
4. Pause/resume functionality
5. Bookmark important moments during recording
6. Export audio files
7. Multiple microphone input support

## Testing

To test the recording feature:

1. Navigate to a visit documentation page:
   ```
   http://localhost:3000/provider/visits/[visit-id]
   ```

2. Switch to SOAP Notes tab (if not already there)

3. Look for the red "Record" button on the left side

4. Click "Record" and grant microphone permission

5. Speak for 10-15 seconds

6. Click "Stop"

7. Click "Transcribe Recording"

8. Wait for transcription to complete

9. Review the transcription preview

10. Click "Generate SOAP Notes"

11. Verify SOAP sections populate correctly

## Troubleshooting

### Common Issues

**Microphone not working:**
- Check browser permissions
- Ensure microphone is not being used by another application
- Check system sound settings

**Transcription fails:**
- Check backend API is running
- Verify audio file size is under limit (50MB)
- Check network connectivity

**No audio visualizer:**
- This is a visual enhancement only
- Recording still works without it
- Check browser console for Web Audio API errors

**Button not appearing:**
- Check browser console for component errors
- Verify RecordingControls component is imported
- Ensure visitId prop is being passed correctly

## Support

For issues or questions:
1. Check browser console for errors
2. Review backend logs: `docker-compose logs api`
3. Verify all containers are running: `docker-compose ps`
4. Check this documentation for workflow details

---

**Last Updated**: 2025-11-29
**Version**: 1.0
**Author**: Healthcare App Development Team
