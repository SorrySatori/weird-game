// Test script to verify the fungal_master sprite loading
const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    scene: {
        preload: preload,
        create: create
    }
};

const game = new Phaser.Game(config);

function preload() {
    // Load the fungal_master sprite
    this.load.spritesheet('fungal_master', 'assets/images/characters/fungal_master.png', { 
        frameWidth: 32, 
        frameHeight: 32 
    });
    
    // Load a test sprite for comparison
    this.load.spritesheet('priest', 'assets/images/characters/priest.png', { 
        frameWidth: 32, 
        frameHeight: 32 
    });
}

function create() {
    // Display the fungal_master sprite
    console.log('Creating fungal_master sprite...');
    const master = this.add.sprite(200, 300, 'fungal_master');
    master.setScale(4);
    
    // Create animation
    this.anims.create({
        key: 'master-idle',
        frames: this.anims.generateFrameNumbers('fungal_master', { start: 0, end: 3 }),
        frameRate: 4,
        repeat: -1
    });
    
    // Play animation
    master.play('master-idle');
    
    // Add text
    this.add.text(200, 400, 'Fungal Master', {
        fontSize: '20px',
        fill: '#ffffff'
    }).setOrigin(0.5);
    
    // Display the priest sprite for comparison
    console.log('Creating priest sprite...');
    const priest = this.add.sprite(600, 300, 'priest');
    priest.setScale(4);
    
    // Create animation
    this.anims.create({
        key: 'priest-idle',
        frames: this.anims.generateFrameNumbers('priest', { start: 0, end: 3 }),
        frameRate: 4,
        repeat: -1
    });
    
    // Play animation
    priest.play('priest-idle');
    
    // Add text
    this.add.text(600, 400, 'Priest (Reference)', {
        fontSize: '20px',
        fill: '#ffffff'
    }).setOrigin(0.5);
    
    // Log sprite information
    console.log('Fungal Master Sprite:', master);
    console.log('Priest Sprite:', priest);
}
