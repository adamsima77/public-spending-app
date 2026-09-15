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
        Schema::create('lot_cpv', function (Blueprint $table) {
           $table->foreignId('notice_lot_id')->constrained('notice_lots')->cascadeOnDelete();
           $table->string('cpv_code', 10);
           $table->foreign('cpv_code')->references('code')->on('cpv_codes')->cascadeOnDelete();
           $table->primary(['notice_lot_id', 'cpv_code']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('lot_cpv');
    }
};
