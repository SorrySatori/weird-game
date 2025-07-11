// Transition scene between Intro and Entry
class TransitionScene extends Phaser.Scene {
    constructor() {
        super({ key: 'TransitionScene' });
    }

    create() {
        // Create a black background
        this.add.rectangle(0, 0, this.scale.width, this.scale.height, 0x000000)
            .setOrigin(0, 0);

        // Add transition text
        const transitionText = this.add.text(
            this.scale.width / 2, 
            this.scale.height / 2,
            'After days of travel, you finally arrive to the city of Upper Morkezela...',
            {
                fontSize: '24px',
                fill: '#ffffff',
                align: 'center',
                wordWrap: { width: this.scale.width * 0.8 }
            }
        ).setOrigin(0.5);

        // Add fade-in effect
        transitionText.setAlpha(0);
        this.tweens.add({
            targets: transitionText,
            alpha: 1,
            duration: 2000,
            ease: 'Linear',
            onComplete: () => {
                // Wait for 3 seconds, then fade out
                this.time.delayedCall(3000, () => {
                    this.tweens.add({
                        targets: transitionText,
                        alpha: 0,
                        duration: 2000,
                        ease: 'Linear',
                        onComplete: () => {
                            // Transition to EntryScene
                            this.cameras.main.fadeOut(1000, 0, 0, 0);
                            this.cameras.main.once('camerafadeoutcomplete', () => {
                                this.scene.start('EntryScene');
                            });
                        }
                    });
                });
            }
        });

        // Allow skipping with space or click
        const skipScene = () => {
            this.tweens.killAll();
            this.cameras.main.fadeOut(500, 0, 0, 0);
            this.cameras.main.once('camerafadeoutcomplete', () => {
                this.scene.start('EntryScene');
            });
        };

        this.input.keyboard.once('keydown-SPACE', skipScene);
        this.input.once('pointerdown', skipScene);
    }
}

export default TransitionScene;
