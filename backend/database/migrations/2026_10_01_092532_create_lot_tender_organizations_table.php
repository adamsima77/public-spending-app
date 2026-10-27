<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('lot_tender_organizations', function (Blueprint $table) {
            $table->id();
            $table->foreignId('lot_tender_id')->constrained('lot_tenders')->cascadeOnDelete();
            $table->foreignId('organization_id')->constrained('organizations')->cascadeOnDelete();
            $table->timestamps();

            $table->unique(['lot_tender_id', 'organization_id']);
            $table->index('organization_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('lot_tender_organizations');
    }
};