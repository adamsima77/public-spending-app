<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('lot_suppliers', function (Blueprint $table) {
            $table->id();
            $table->foreignId('lot_id')->constrained('notice_lots')->cascadeOnDelete();
            $table->foreignId('organization_id')->constrained('organizations')->cascadeOnDelete();
            $table->decimal('winning_amount', 14, 2)->nullable();
            $table->timestamps();
            $table->unique(['lot_id', 'organization_id']);
            $table->index('organization_id');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('lot_suppliers');
    }
};
