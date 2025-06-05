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
        { speaker: 'NARRATOR', text: 'In the Rootdepths of Obazoba, the spores speak.' },
        { speaker: 'ACHPRIEST VARHUN', text: 'A tremor through the network. Not rot. Not bloom. A call.' },
        { speaker: 'ACHPRIEST TYNRI', text: 'From the surface. From Upper Morkezela.' },
        { speaker: 'ACHPRIEST VARHUN', text: 'We must respond, though we do not know who speaks.' },
        { speaker: 'ACHPRIEST RHULL', text: 'The Egg Cathedral sits atop the old sporespire. If a call came, it likely came from there… or from beneath it.' },
        { speaker: 'ACHPRIEST VARHUN', text: 'Let our emissary walk the deadroot path. Let the priest rise.' },
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
  
      this.input.keyboard.on('keydown-SPACE', () => {
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
        this.scene.start('EntryScene'); // Move to main game
      }
    }
  }
  
  export default IntroScene;
  