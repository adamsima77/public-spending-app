<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('lot_tenders', function (Blueprint $table) {
            $table->id();
            $table->string('notice_id', 250);
            $table->string('lot_reference', 64);
            $table->foreignId('lot_id')->nullable()->constrained('notice_lots')->nullOnDelete();
            $table->string('tender_ref', 64);
            $table->decimal('tender_value', 14, 2)->nullable();
            $table->string('tender_currency', 10)->nullable();
            $table->string('tendering_party_ref', 64)->nullable();
            $table->integer('rank')->nullable();
            $table->string('subcontracting', 16)->nullable();
            $table->jsonb('extra_fields')->nullable();
            $table->timestamps();
            $table->index('lot_id');
            $table->unique(['notice_id', 'tender_ref'], 'lot_tenders_notice_id_tender_ref_unique');
            $table->index(['notice_id', 'lot_reference'], 'lot_tenders_notice_id_lot_reference_index');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('lot_tenders');
    }
};