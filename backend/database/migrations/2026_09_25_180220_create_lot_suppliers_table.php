<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class () extends Migration {
    public function up(): void
    {
        Schema::create('lot_suppliers', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('lot_id')->constrained('notice_lots')->cascadeOnDelete();
            $table->foreignId('organization_id')->constrained('organizations')->cascadeOnDelete();
            $table->foreignId('notice_record_id')->nullable()->constrained('notices')->restrictOnDelete();
            $table->decimal('winning_amount', 14, 2)->nullable();
            $table->char('winning_currency', 3)->nullable();
            $table->timestamps();

            $table->unique(['lot_id', 'organization_id']);
            $table->index('organization_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('lot_suppliers');
    }
};
