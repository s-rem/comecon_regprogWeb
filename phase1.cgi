#!/usr/bin/perl
use lib ((getpwuid($<))[7]) . '/local/lib/perl5';
use strict;
use CGI;
use CGI::Session;
use CGI::Carp qw(fatalsToBrowser); 
use HTML::Template;
use HTML::FillInForm;
use SFCON::Register;
use SFCON::Register_db;

my $c_not_fill = 'bgcolor="red"';

my $register = SFCON::Register->new;
my $cgi=CGI->new;
my $sid=$cgi->param('ID')||$cgi->cookie('ID')||undef;
#1.cookieからCGISESSIDを探す
#2.cookieから取れなかったらurlパラメータを探す．
#3.どちらも取得できなかったらundef．
my $session=CGI::Session->new(undef,$sid,{Directory=>$register->session_dir()});

my $input_page=HTML::Template->new(filename => 'phase1-tmpl.html');
my $form_out = HTML::FillInForm->new;
my $html_out;

#4.取得したセッションidが有効ならそのまま．無効なら別のidを発番．

if(defined $sid && $sid eq $session->id){
#cookieかurlパラメータから値を取得でき，かつ有効なid
	$input_page->param(ID => $sid);

	if($session->param('phase') ne '1-2' || $cgi->param('self') ne 'true') {
        # 申し込み画面初期表示
		$session->param('phase','1-2');
		$html_out = $form_out->fill(
			scalarref => \$input_page->output,
			target => "mailform",
			fobject => $session
		);
	} else {
        # 申し込み受付時チェック

		if ( _input_check($cgi, $input_page) ) {
            # 入力内容不備時 申込画面再表示
			$html_out = $form_out->fill(
				scalarref => \$input_page->output,
				target => "mailform",
				fobject => $cgi
			);
		} else {
            # 申し込み成功 
			$session->save_param($cgi);
			$html_out = $form_out->fill(
				scalarref => \$input_page->output,
				target => "mailform",
				fobject => $cgi
			);
			if($cgi->cookie('ID') eq  $session->id){
				print $cgi->redirect('./phase2.cgi');
			} else {
				print $cgi->redirect('./phase2.cgi?ID='. $sid);
			}
			exit;
		}
	}
	my $cookie_path = $ENV{SCRIPT_NAME};
	$cookie_path =~ s/[^\/]+$//g ;
	my $cookie = $cgi->cookie(-name => "ID", -value   => "$sid", -expires => "+3h", -path => "$cookie_path");

	print $cgi->header(-charset=>'UTF-8', -expires=>'now', -cookie=>$cookie);
	print "\n\n".$html_out;

}else{
    # セッションタイムアウトなど
	if(defined $sid && $sid ne $session->id){
		  $session->close;
		  $session->delete;
	}
	print $cgi->redirect('./error.html');
}
exit;

sub _input_check {
	my ($cgi, $input_page) = @_;
	my $input_check = 0;
	
# 主催者情報
    # 名前
	if($cgi->param('p1_name') eq ''){
		$input_page->param(C_P1_NAME => $c_not_fill);
		$input_check = 1;
	}
    # メールアドレス
	if($cgi->param('email') eq ''){
		$input_page->param(C_CO_EMAIL => $c_not_fill);
		$input_check = 1;
	}
    # 参加登録番号
	if($cgi->param('reg_num') eq ''){
		$input_page->param(C_CO_REG_NUMBER => $c_not_fill);
		$input_check = 1;
	}
    # 電話番号、FAX番号、携帯番号は省略可能

# 企画情報
    # 企画名称
	if($cgi->param('pg_name') eq ''){
		$input_page->param(C_CO_PG_NAME => $c_not_fill);
		$input_check = 1;
	}
    # 企画名称フリガナ
	if($cgi->param('pg_name_f') eq ''){
		$input_page->param(C_CO_PG_NAME_F => $c_not_fill);
		$input_check = 1;
	}
    # 企画種別
	if($cgi->param('pg_kind') eq ''){
		$input_page->param(C_CO_PG_KIND => $c_not_fill);
		$input_check = 1;
	}
	if($cgi->param('pg_kind') eq 'K-X1' && $cgi->param('pg_kind2') eq ''){
		$input_page->param(C_CO_PG_KIND => $c_not_fill);
		$input_check = 1;
	}
	if($cgi->param('pg_kind') ne 'K-X1' && $cgi->param('pg_kind2') ne ''){
		$input_page->param(C_CO_PG_KIND => $c_not_fill);
		$input_check = 1;
	}
    # 希望場所
	if($cgi->param('pg_place') eq ''){
		$input_page->param(C_CO_PG_PLACE => $c_not_fill);
		$input_check = 1;
	}
	if($cgi->param('pg_place') eq 'P-X1' && $cgi->param('pg_place2') eq ''){
		$input_page->param(C_CO_PG_PLACE => $c_not_fill);
		$input_check = 1;
	}
	if($cgi->param('pg_place') ne 'P-X1' && $cgi->param('pg_place2') ne ''){
		$input_page->param(C_CO_PG_PLACE => $c_not_fill);
		$input_check = 1;
	}
    # 希望場所レイアウト
	if($cgi->param('pg_layout') eq '9' && $cgi->param('pg_layout2') eq ''){
		$input_page->param(C_CO_PG_PLACE => $c_not_fill);
		$input_check = 1;
	}
	if($cgi->param('pg_layout') ne '9' && $cgi->param('pg_layout2') ne ''){
		$input_page->param(C_CO_PG_PLACE => $c_not_fill);
		$input_check = 1;
	}
    # 希望日時
	if($cgi->param('pg_time') eq ''){
		$input_page->param(C_CO_PG_TIME => $c_not_fill);
		$input_check = 1;
	}
	if($cgi->param('pg_time') eq 'T-X1' && $cgi->param('pg_time2') eq ''){
		$input_page->param(C_CO_PG_TIME => $c_not_fill);
		$input_check = 1;
	}
	if($cgi->param('pg_time') ne 'T-X1' && $cgi->param('pg_time2') ne ''){
		$input_page->param(C_CO_PG_TIME => $c_not_fill);
		$input_check = 1;
	}
    # 希望コマ数
	if($cgi->param('pg_koma') eq ''){
		$input_page->param(C_CO_PG_KOMA => $c_not_fill);
		$input_check = 1;
	}
	if($cgi->param('pg_koma') eq 'TK-X1' && $cgi->param('pg_koma2') eq ''){
		$input_page->param(C_CO_PG_KOMA => $c_not_fill);
		$input_check = 1;
	}
	if($cgi->param('pg_koma') ne 'TK-X1' && $cgi->param('pg_koma2') ne ''){
		$input_page->param(C_CO_PG_KOMA => $c_not_fill);
		$input_check = 1;
	}
    # 予想参加者
	if($cgi->param('pg_ninzu') eq ''){
		$input_page->param(C_CO_PG_NINZU => $c_not_fill);
		$input_check = 1;
	}
    # 内容説明
	if($cgi->param('pg_naiyou') eq '' || $cgi->param('pg_naiyou_k') eq ''){
		$input_page->param(C_CO_PG_NAIYOU => $c_not_fill);
		$input_check = 1;
	}

# 出演者情報
	if($cgi->param('pp1_name') ne '' || $cgi->param('pp1_name_f') ne ''){
		if($cgi->param('pp1_name') eq '' || $cgi->param('pp1_con') eq '' || $cgi->param('pp1_grq') eq ''){
			$input_page->param(C_CO_PG_GUEST1 => $c_not_fill);
			$input_check = 1;
		}
	}

	if($cgi->param('pp2_name') ne '' || $cgi->param('pp2_name_f') ne ''){
		if($cgi->param('pp2_name') eq '' || $cgi->param('pp2_con') eq '' || $cgi->param('pp2_grq') eq ''){
			$input_page->param(C_CO_PG_GUEST2 => $c_not_fill);
			$input_check = 1;
		}
	}

	if($cgi->param('pp3_name') ne '' || $cgi->param('pp3_name_f') ne ''){
		if($cgi->param('pp3_name') eq '' || $cgi->param('pp3_con') eq '' || $cgi->param('pp3_grq') eq ''){
			$input_page->param(C_CO_PG_GUEST3 => $c_not_fill);
			$input_check = 1;
		}
	}

	if($cgi->param('pp4_name') ne '' || $cgi->param('pp4_name_f') ne ''){
		if($cgi->param('pp4_name') eq '' || $cgi->param('pp4_con') eq '' || $cgi->param('pp4_grq') eq ''){
			$input_page->param(C_CO_PG_GUEST4 => $c_not_fill);
			$input_check = 1;
		}
	}

	if($cgi->param('pp5_name') ne '' || $cgi->param('pp5_name_f') ne ''){
		if($cgi->param('pp5_name') eq '' || $cgi->param('pp5_con') eq '' || $cgi->param('pp5_grq') eq ''){
			$input_page->param(C_CO_PG_GUEST5 => $c_not_fill);
			$input_check = 1;
		}
	}

	if($cgi->param('pp6_name') ne '' || $cgi->param('pp6_name_f') ne ''){
		if($cgi->param('pp6_name') eq '' || $cgi->param('pp6_con') eq '' || $cgi->param('pp6_grq') eq ''){
			$input_page->param(C_CO_PG_GUEST6 => $c_not_fill);
			$input_check = 1;
		}
	}

	if($cgi->param('pp7_name') ne '' || $cgi->param('pp7_name_f') ne ''){
		if($cgi->param('pp7_name') eq '' || $cgi->param('pp7_con') eq '' || $cgi->param('pp7_grq') eq ''){
			$input_page->param(C_CO_PG_GUEST7 => $c_not_fill);
			$input_check = 1;
		}
	}

	if($cgi->param('pp8_name') ne '' || $cgi->param('pp8_name_f') ne ''){
		if($cgi->param('pp8_name') eq '' || $cgi->param('pp8_con') eq '' || $cgi->param('pp8_grq') eq ''){
			$input_page->param(C_CO_PG_GUEST8 => $c_not_fill);
			$input_check = 1;
		}
	}

	return($input_check);
}

#end
