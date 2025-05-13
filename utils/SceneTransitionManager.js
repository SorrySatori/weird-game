export default class SceneTransitionManager {
    constructor(scene) {
        this.scene = scene;
    }

    createTransitionZone(x, y, width, height, direction, targetScene, walkX, walkY) {
        // Create the interactive zone
        const zone = this.scene.add.zone(x, y, width, height)
            .setInteractive({ useHandCursor: true })
            .setOrigin(0.5)
            .setDepth(10);

        // Add the hover arrow effect
        this.addHoverEffect(zone, direction);

        // Add the transition logic
        zone.on('pointerdown', () => {
            if (this.scene.isTransitioning) return;
            this.scene.isTransitioning = true;

            const priest = this.scene.priest;
            priest.play('walk');
            this.scene.tweens.killTweensOf(priest);
            
            this.scene.tweens.add({
                targets: priest,
                x: walkX,
                y: walkY,
                duration: 1000,
                onComplete: () => {
                    this.scene.cameras.main.fadeOut(800, 0, 0, 0);
                    this.scene.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.scene.start(targetScene);
                        this.scene.isTransitioning = false;
                    });
                }
            });
        });

        return zone;
    }

    addHoverEffect(zone, direction) {
        const arrow = this.scene.add.sprite(zone.x, zone.y, 'arrow')
            .setScale(0.5)
            .setTint(0x7fff8e)
            .setAlpha(0)
            .setDepth(20);

        // Set arrow rotation based on direction
        switch(direction) {
            case 'left': arrow.setAngle(180); break;
            case 'right': arrow.setAngle(0); break;
            case 'up': arrow.setAngle(270); break;
            case 'down': arrow.setAngle(90); break;
        }

        // Add hover effects
        zone.on('pointerover', () => {
            this.scene.tweens.add({
                targets: arrow,
                alpha: { from: 0.4, to: 1 },
                scale: { from: 0.4, to: 0.6 },
                duration: 800,
                ease: 'Sine.easeInOut',
                yoyo: true,
                repeat: -1
            });
        });

        zone.on('pointerout', () => {
            this.scene.tweens.killTweensOf(arrow);
            arrow.setAlpha(0);
            arrow.setScale(0.5);
        });
    }
}
