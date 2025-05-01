export default class SymbiontSystem {
    constructor(scene) {
        this.scene = scene;
        this.symbionts = new Map();
        this.maxSlots = 3;
        this.unlockedSlots = 1;
        this.lastMessageTime = 0;
        this.messageInterval = 30000; // 30 seconds minimum between messages
    }

    addSymbiont(id, data) {
        if (this.symbionts.size >= this.unlockedSlots) {
            return false;
        }
        this.symbionts.set(id, {
            ...data,
            lastSpoke: 0
        });
        return true;
    }

    removeSymbiont(id) {
        return this.symbionts.delete(id);
    }

    unlockSlot() {
        if (this.unlockedSlots < this.maxSlots) {
            this.unlockedSlots++;
            return true;
        }
        return false;
    }

    checkDecayGrowthEffects(decay, growth) {
        if (this.symbionts.has('thorne-still')) {
            if (growth > 80) {
                this.removeSymbiont('thorne-still');
                return {
                    type: 'leave',
                    message: 'The overwhelming growth forces Thorne-Still to leave your body...'
                };
            }
            // Strengthen with decay
            const symbiont = this.symbionts.get('thorne-still');
            symbiont.power = Math.min(100, decay);
        }
        return null;
    }

    getRandomMessage(symbiontId) {
        const now = Date.now();
        if (now - this.lastMessageTime < this.messageInterval) {
            return null;
        }

        const symbiont = this.symbionts.get(symbiontId);
        if (!symbiont || now - symbiont.lastSpoke < this.messageInterval) {
            return null;
        }

        if (symbiontId === 'thorne-still') {
            const messages = [
                "In the spaces between reality, truth flows like mercury...",
                "The patterns... they speak of what was and what will be...",
                "I see the threads that bind this world together...",
                "The void whispers secrets to those who listen...",
                "Time is but a circle in the eyes of the eternal...",
            ];
            const message = messages[Math.floor(Math.random() * messages.length)];
            symbiont.lastSpoke = now;
            this.lastMessageTime = now;
            return message;
        }
        return null;
    }

    sutureReality() {
        if (!this.symbionts.has('thorne-still')) {
            return false;
        }
        const symbiont = this.symbionts.get('thorne-still');
        return symbiont.power > 30; // Only works if decay is at least 30
    }
}
