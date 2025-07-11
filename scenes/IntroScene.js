// Phaser.js cutscene implementation: "The Myceliar Summons"
// This assumes you have a scene set up, a dialogue system in place, and backgrounds prepared

class IntroScene extends Phaser.Scene {
    constructor() {
      super({ key: 'IntroScene' });
    }
  
    preload() {
      // Load background images and any other assets
      this.load.image('fungalCouncil1', 'assets/images/backgrounds/fungal_council_1.png');
      this.load.image('mycelialOverlay', 'assets/images/backgrounds/mycelial_overlay.png');
    //   this.load.audio('signalPulse', 'assets/audio/signal_pulse.wav');
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
      this.dialogues = [
        { speaker: 'NARRATOR', text: 'In the underground temple of Obazoba, the Spore Council is gathered.' },
        { speaker: 'ACHPRIEST VARHUN', text: 'A distress call through the myceliar network. Not rot. Not bloom. A cry for help.' },
        { speaker: 'ACHPRIEST TYNRI', text: 'From the surface. From city of Upper Morkezela.' },
        { speaker: 'ACHPRIEST VARHUN', text: 'We must respond, though we do not know who speaks.' },
        { speaker: 'ACHPRIEST RHULL', text: `The Egg Cathedral is the place where we should go. The Bishop would know more. She has been monitoring what's going on in the city.` },
        { speaker: 'ACHPRIEST VARHUN', text: 'Summon master Thaal to walk the deadroot path. Let the fungal emissary rise.' },
        { speaker: 'ACHPRIEST TYNRI', text: 'He could be a capable investigator, true. But I have a notion that his apprentice is... rather troublesome person, I must say.' },
        { speaker: 'ACHPRIEST RHULL', text: 'He is... well, he is Thaal apprentice. I do not know much about him, but I do know that he is not the most... sharpest mushroom in the forest.' },
        { speaker: 'ACHPRIEST RHULL', text: 'At least this time we have hidden the ceremonial oils.' },
        { speaker: 'ACHPRIEST TYNRI', text: 'And locked the fungal archive. Twice.' },
        { speaker: 'ACHPRIEST VARHUN', text: 'Let the master Thaal rise - quietly, if possible. Let him to find the Bishop from Upper Morkezela and discover the source of this distress call. The apprentice is his responsibility.' },
      ];
  
      // Overlay animation
      this.overlay = this.add.image(400, 300, 'mycelialOverlay')
        .setBlendMode('ADD')
        .setAlpha(0.15);
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
  