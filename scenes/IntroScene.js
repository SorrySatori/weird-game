// Phaser.js cutscene implementation: "The Myceliar Summons"
// This assumes you have a scene set up, a dialogue system in place, and backgrounds prepared

import { fitBackground } from '../utils/fitBackground.js';
import LanguageSystem from '../systems/LanguageSystem.js';

class IntroScene extends Phaser.Scene {
    constructor() {
      super({ key: 'IntroScene' });
    }
  
    preload() {
      // Load background images and any other assets
      this.load.image('fungalCouncil1', 'assets/images/backgrounds/fungal_council_1.png');
      this.load.image('mycelialOverlay', 'assets/images/backgrounds/mycelial_overlay.png');
      this.load.audio('introMusic', 'assets/sounds/obazoba-hall.mp3');
    }
  
    create() {
      // Show static fungal chamber
      const bg = this.add.image(0, 0, 'fungalCouncil1').setOrigin(0, 0);

      // Calculate scale based on canvas size
      const scaleX = this.scale.width / bg.width;
      const scaleY = this.scale.height / bg.height;
      const scale = Math.min(scaleX, scaleY);
      
      bg.setScale(scale);
      bg.setPosition(
        (this.scale.width - bg.width * scale) / 2,
        (this.scale.height - bg.height * scale) / 2
      );
  
      // Begin Dialogue Sequence
      this.dialogueIndex = 0;
      // Localized in lang/*/intro.js (array of {speaker, text})
      this.dialogues = LanguageSystem.getInstance().t('intro.dialogues');
  
      // Overlay animation
      this.overlay = this.add.image(this.scale.width / 2, this.scale.height / 2, 'mycelialOverlay')
        .setBlendMode('ADD')
        .setAlpha(0.15);
      fitBackground(this, this.overlay); // whole overlay fitted to the 1067×600 canvas
      this.tweens.add({
        targets: this.overlay,
        alpha: 0.3,
        yoyo: true,
        repeat: -1,
        duration: 1500
      });
  
      // Text UI
      this.dialogueBox = this.add.rectangle(400, 540, 760, 100, 0x1e1e1e, 0.85).setOrigin(0.5);
      this.dialogueText = this.add.text(50, 500, '', { fontSize: '16px', fill: '#ffffff', wordWrap: { width: 700 } });
      
      // Add "Press SPACE" prompt
      this.promptText = this.add.text(400, 570, 'Press SPACE to continue', { 
        fontSize: '14px', 
        fill: '#7fff8e',
        fontStyle: 'italic'
      }).setOrigin(0.5);
      
      // Add a pulsating effect to the prompt
      this.tweens.add({
        targets: this.promptText,
        alpha: { from: 0.5, to: 1 },
        duration: 800,
        ease: 'Sine.easeInOut',
        yoyo: true,
        repeat: -1
      });
  
      this.input.keyboard.on('keydown-SPACE', () => {
        this.nextDialogue();
      });
      
      // Also allow clicking anywhere to advance dialog
      this.input.on('pointerdown', () => {
        this.nextDialogue();
      });
  
      this.nextDialogue();
      this.sound.stopAll();

      if (!this.backgroundMusic) {
        this.backgroundMusic = this.sound.add('introMusic', { loop: true });
    }
    this.sceneMusic = this.sound.add('introMusic', { loop: true });
    this.sceneMusic.play();
    }
  
    nextDialogue() {
      if (this.dialogueIndex < this.dialogues.length) {
        const line = this.dialogues[this.dialogueIndex];
        this.dialogueText.setText(`${line.speaker}: ${line.text}`);
        this.dialogueIndex++;
      } else {
        // Fade out and transition to the TransitionScene
        this.cameras.main.fadeOut(1000, 0, 0, 0);
        this.cameras.main.once('camerafadeoutcomplete', () => {
          this.scene.start('TransitionScene');
        });
      }
    }
  }
  
  export default IntroScene;
  